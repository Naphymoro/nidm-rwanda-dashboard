"""Compare Ollama models on held-out journeys the training never saw: the gate a fine-tuned version must pass.

Scores per model, on a fixed stratified sample of held-out questions:
- clean: replies with no number the engine did not produce and no forbidden claim word (the Studio's own check);
- traps: forecast, cause and advice questions answered as the engine would (not a forecast / cannot show / not advice);
- key_numbers: share of the engine explanation's numbers that the reply states (explain questions);
- seconds and GPU joules per reply.

    python evaluate.py --data heldout.jsonl --models qwen3:1.7b ndim-qwen3-1.7b:v1 --host http://127.0.0.1:11435
    python evaluate.py --tools-data tools_heldout.jsonl --tools-schema tools_schema.json --models ... (tool use)

Tool use, on held-out Studio situations: the right tool with exactly the right arguments (the question verbatim, the
stage, the notes unchanged), and no tool at all where the decision is the researcher's (the reply points to the card).
"""
import argparse
import json
import random
import re
import subprocess
import sys
import threading
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend' / 'app'))
import agent_checks  # noqa: E402  (pure Python; no engine dependencies)

TRAP_OK = {'forecast': re.compile(r'\b(not a forecast|illustrative)\b', re.I),
           'cause': re.compile(r"\b(cannot show|can't show|cannot tell|does not show|doesn't show|not causal|cannot say)\b", re.I),
           'advice': re.compile(r'\b(not advice|not (?:a )?recommendations?|options for (?:your team to )?discuss)', re.I)}
PER_KIND = {'explain': 40, 'cause': 20, 'forecast': 20, 'advice': 20}


class Power:
    def __init__(self):
        self.samples = []
        self.proc = subprocess.Popen(['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits', '-lms', '100'],
                                     stdout=subprocess.PIPE, text=True)
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.proc.stdout:
            try:
                self.samples.append((time.time(), float(line)))
            except ValueError:
                pass

    def joules(self, start, end):
        window = [w for t, w in self.samples if start <= t <= end]
        return sum(window) / len(window) * (end - start) if window else 0.0


def ask(host, model, messages, tools=None, full=False):
    body = {'model': model, 'messages': messages, 'stream': False, 'think': False,
            'options': {'temperature': 0, 'num_ctx': 8192, 'num_predict': 400}}
    if tools:
        body['tools'] = tools
    req = urllib.request.Request(host + '/api/chat', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=600) as response:
        message = json.loads(response.read())['message']
    return message if full else message['content']


def tool_score(model, rows, host, tools):
    """Share of held-out tool situations handled exactly right, per kind."""
    out = defaultdict(list)
    for row in rows:
        *history, target = row['messages']
        message = ask(host, model, history, tools, full=True)
        calls = [c['function'] for c in message.get('tool_calls') or []]
        if row['kind'].startswith('tool_'):
            want = target['tool_calls'][0]['function']
            got = next((c for c in calls if c['name'] == want['name']), None)
            args = got['arguments'] if got else None
            args = json.loads(args) if isinstance(args, str) else args
            if row['kind'] == 'tool_records':
                ok = bool(args) and [r.get('text', '').strip() for r in args.get('records', [])] == [r['text'] for r in want['arguments']['records']]
            else:
                ok = got is not None and all(args.get(key) == value for key, value in want['arguments'].items())
        elif row['kind'] == 'next_answer':  # answered from the facts in the prompt, naming the next stage, no tool
            title = re.search(r'Next is \d+\. ([^:]+):', target['content']).group(1)
            ok = not calls and title.lower() in (message.get('content') or '').lower()
        else:  # no_fake_*: the researcher's decision: no action, and the reply points to the card
            ok = not calls and 'card' in (message.get('content') or '').lower()
        out[row['kind']].append(ok)
    return {kind: round(sum(v) / len(v), 3) for kind, v in out.items()} | {'all': round(sum(sum(v) for v in out.values()) / len(rows), 3)}


def sample(rows, seed=3):
    rng, by_kind = random.Random(seed), defaultdict(list)
    for row in rows:
        by_kind[row['kind']].append(row)
    picked = []
    for kind, n in PER_KIND.items():
        rng.shuffle(by_kind[kind])
        picked += by_kind[kind][:n]
    return picked


def score(model, rows, host, power):
    out = defaultdict(list)
    examples = []
    for row in rows:
        system, question, reference = (m['content'] for m in row['messages'])
        start = time.time()
        reply = ask(host, model, [{'role': 'system', 'content': system}, {'role': 'user', 'content': question}])
        end = time.time()
        reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.S).strip()
        found = agent_checks.check(reply, agent_checks.known_numbers(system, question))
        out['clean'].append(found is None)
        out['seconds'].append(end - start)
        out['joules'].append(power.joules(start, end))
        if row['kind'] in TRAP_OK:
            out['traps'].append(bool(TRAP_OK[row['kind']].search(reply)))
        if row['kind'] == 'explain':
            wanted = set(agent_checks.NUMBER.findall(reference))
            got = set(agent_checks.NUMBER.findall(reply))
            out['key_numbers'].append(len(wanted & got) / len(wanted) if wanted else 1.0)
        if len(examples) < 6:
            examples.append({'kind': row['kind'], 'stage': row['stage'], 'question': question, 'reply': reply[:500], 'check': found})
    mean = lambda values: round(sum(values) / len(values), 3) if values else None
    return {key: mean(values) for key, values in out.items()} | {'n': len(rows), 'examples': examples}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data')
    parser.add_argument('--tools-data')
    parser.add_argument('--tools-schema')
    parser.add_argument('--models', nargs='+', required=True)
    parser.add_argument('--host', default='http://127.0.0.1:11435')
    parser.add_argument('--out', default='evaluation.json')
    args = parser.parse_args()
    if args.tools_data:
        tools = json.load(open(args.tools_schema, encoding='utf-8'))
        rows = [json.loads(line) for line in open(args.tools_data, encoding='utf-8')]
        results = {model: tool_score(model, rows, args.host, tools) for model in args.models}
        for model, result in results.items():
            print(model, json.dumps(result), flush=True)
        Path(args.out).write_text(json.dumps(results, indent=1))
        return
    rows = sample([json.loads(line) for line in open(args.data, encoding='utf-8')])
    power, results = Power(), {}
    for model in args.models:
        results[model] = score(model, rows, args.host, power)
        print(model, json.dumps({k: v for k, v in results[model].items() if k != 'examples'}), flush=True)
        Path(args.out).write_text(json.dumps(results, indent=1, ensure_ascii=False))
    power.proc.terminate()


if __name__ == '__main__':
    main()
