"""Training examples from the researchers' feedback: replies they approved (thumbs-up) or corrected in the Studio.

Only researcher-checked answers: agent_learning.dataset() leaves out thumbs-down-only replies, and a reply the engine
flagged can only be learned in its corrected form. Each example gets a real Studio system prompt (taken from the tool
examples, as in make_replay.py), so the model sees lessons as it sees them in use. The lessons file is only read.

    python export_lessons.py --lessons ~/ndim-data/learning/lessons.json --system-from tools.jsonl --out lessons.jsonl

--lessons takes the lessons.json file or the NDIM data folder that holds learning/lessons.json. A missing file gives an
empty output (a first run has no feedback yet).
"""
import argparse
import json
import os
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ['NDIM_DATA_DIR'] = tempfile.mkdtemp(prefix='ndim-lessons-')  # never the researcher's folder: it is only read
from app import agent_learning  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lessons', help='lessons.json, or the NDIM data folder that holds learning/lessons.json')
    parser.add_argument('--system-from', required=True, help='tool examples file; Studio system prompts are taken from it')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    path = Path(args.lessons).expanduser() if args.lessons else None
    if path and path.is_dir():
        path = path / 'learning' / 'lessons.json'
    rows = []
    if path and path.exists():
        agent_learning._file = lambda: path
        systems = [json.loads(line)['messages'][0]['content'] for line in open(args.system_from, encoding='utf-8')
                   if json.loads(line)['kind'] == 'tool_propose']
        rng = random.Random(5)
        for row in agent_learning.dataset():
            row['messages'][0]['content'] = rng.choice(systems)
            rows.append(row | {'kind': 'lesson', 'lesson_kind': row['kind']})
    with open(args.out, 'w', encoding='utf-8') as out:
        out.writelines(json.dumps(row, ensure_ascii=False) + '\n' for row in rows)
    print(f'{len(rows)} researcher-checked lessons from {path or "(no lessons file)"} -> {args.out}')


if __name__ == '__main__':
    main()
