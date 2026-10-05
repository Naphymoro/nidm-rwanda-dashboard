"""One command from fresh data to a gated model: dataset -> train -> convert -> create -> evaluate -> gate.

    python scripts/local_ai_training/pipeline.py --engine-python .venv/bin/python --lessons ~/ndim-data
    python scripts/local_ai_training/pipeline.py --version v4 --from-stage evaluate     (re-run from a stage)
    python scripts/local_ai_training/pipeline.py --version smoke --journeys 2 --tools-journeys 2 --replay-rounds 1 \
        --max-steps 4 --eval-fraction 0.2 --registry /tmp/registry.json --remove-rejected   (smoke test, minutes)

Stages (each writes into WORK/VERSION; a finished stage is skipped when the command is run again, --from-stage re-runs
from there, --to-stage stops early; a resumed run reuses the options saved in run.json unless given again):
- dataset: engine-as-teacher answers and tool situations (make_dataset.py), replay of the base model's everyday answers
  (make_replay.py) and the answers researchers approved or corrected in the Studio (export_lessons.py). Nothing the
  model wrote is learned unless a researcher checked it. Held-out sets (other districts and seeds) are built once and
  then kept fixed, so every version is measured on the same questions.
- train: QLoRA (train_lora.py) and a full-precision merge.
- convert: merged model -> f16 GGUF (llama.cpp; Ollama 0.35 imports safetensors only with MLX).
- create: `ollama create FAMILY:VERSION` in the private Ollama, with the base model's template and parameters.
- evaluate: evaluate.py's answer and tool scores, and the 10-task bench (../local_ai_benchmark), for the candidate, the
  promoted model and the base model. Scores are cached per model digest and held-out set.
- gate: gate.py decides; the verdict, scores, dataset hash and date go into the registry (backend/app/local_models.json),
  which the Studio's model picker reads. A rejected version leaves the promoted one in place and records why.
Every run writes report.md and report.json in its folder.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import gate  # noqa: E402

STAGES = ['dataset', 'train', 'convert', 'create', 'evaluate', 'gate']
HOME = Path.home()
TRAIN_FILES = ['train.jsonl', 'tools.jsonl', 'replay.jsonl', 'lessons.jsonl']
RESUME_FREE = ('from_stage', 'to_stage')  # options never taken from a saved run


def parse(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--version', help='new version tag (default: the next vN after the registry\'s versions)')
    p.add_argument('--from-stage', choices=STAGES)
    p.add_argument('--to-stage', choices=STAGES)
    p.add_argument('--work', default=str(HOME / 'ndim-train' / 'pipeline'))
    p.add_argument('--registry', default=str(ROOT / 'backend' / 'app' / 'local_models.json'))
    p.add_argument('--host', default='http://127.0.0.1:11435', help='the private Ollama')
    p.add_argument('--ollama-bin', default=str(HOME / 'ollama-local' / 'bin' / 'ollama'))
    p.add_argument('--engine-python', default=os.getenv('NDIM_ENGINE_PYTHON') or sys.executable,
                   help="a Python with the backend's dependencies (dataset stage)")
    p.add_argument('--train-python', default=str(HOME / 'ndim-train' / '.venv' / 'bin' / 'python'))
    p.add_argument('--llama-cpp', default=str(HOME / 'ndim-train' / 'llama.cpp'))
    p.add_argument('--base-hf', default='Qwen/Qwen3-1.7B')
    # data
    p.add_argument('--journeys', type=int, default=120)
    p.add_argument('--tools-journeys', type=int, default=60)
    p.add_argument('--replay-rounds', type=int, default=6)
    p.add_argument('--lessons', help='lessons.json or the NDIM data folder holding learning/lessons.json')
    p.add_argument('--heldout', default=str(HOME / 'ndim-train' / 'heldout.jsonl'))
    p.add_argument('--tools-heldout', default=str(HOME / 'ndim-train' / 'tools_v3_heldout.jsonl'))
    # training
    p.add_argument('--lr', type=float, default=1e-4)
    p.add_argument('--max-len', type=int, default=4096)
    p.add_argument('--max-steps', type=int, default=-1)
    p.add_argument('--max-examples', type=int)
    # evaluation and gate
    p.add_argument('--eval-fraction', type=float, default=1.0, help='share of the held-out questions to ask (smoke tests)')
    p.add_argument('--no-bench', action='store_true', help='skip the 10-task bench')
    p.add_argument('--tolerance', type=float, default=gate.TOLERANCE)
    p.add_argument('--overall-tolerance', type=float, default=gate.OVERALL_TOLERANCE)
    p.add_argument('--remove-rejected', action='store_true', help='ollama rm a version the gate rejects')
    p.add_argument('--keep-gguf', action='store_true', help='keep the GGUF after the Ollama import (3.4 GB)')
    args = p.parse_args(argv)
    registry = gate.load_registry(args.registry)
    args.version = args.version or next_version(registry)
    saved = Path(args.work).expanduser() / args.version / 'run.json'
    if saved.exists():  # resume with the options of the first run, unless given again
        given = {a.dest for a in p._actions if any(opt in (argv or sys.argv[1:]) for opt in a.option_strings)}
        old = json.loads(saved.read_text())['args']
        for key, value in old.items():
            if key not in given and key not in RESUME_FREE and hasattr(args, key):
                setattr(args, key, value)
    return args


def next_version(registry):
    numbers = [int(m.group(1)) for v in registry['versions'] if (m := re.search(r':v(\d+)$', v['model']))]
    return f'v{max(numbers, default=0) + 1}'


# ---------------------------------------------------------------- helpers
def sha256(*paths):
    digest = hashlib.sha256()
    for path in paths:
        digest.update(Path(path).read_bytes())
    return digest.hexdigest()


def kinds(path):
    return dict(Counter(json.loads(line)['kind'] for line in open(path, encoding='utf-8')))


def run(cmd, log, cwd=None, env=None):
    print('  $', ' '.join(str(c) for c in cmd), flush=True)
    with open(log, 'a', encoding='utf-8') as out:
        out.write(f'\n$ {" ".join(str(c) for c in cmd)}\n')
        out.flush()
        code = subprocess.call([str(c) for c in cmd], stdout=out, stderr=subprocess.STDOUT, cwd=cwd, env=env)
    if code:
        tail = Path(log).read_text(encoding='utf-8', errors='replace').splitlines()[-25:]
        raise SystemExit(f'command failed ({code}); last lines of {log}:\n' + '\n'.join(tail))


def ollama(host, path, body=None):
    req = urllib.request.Request(host + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read())


def installed(host):
    return {m['name']: m['digest'] for m in ollama(host, '/api/tags')['models']}


def unload_all(host):
    """Free the GPU for training: a model Ollama keeps loaded (the replay's) leaves too little memory."""
    try:
        for model in ollama(host, '/api/ps')['models']:
            ollama(host, '/api/generate', {'model': model['name'], 'keep_alive': 0})
    except OSError:
        pass  # Ollama not running: nothing loaded


def engine_env():
    env = dict(os.environ)
    for name in ('NDIM_DATA_DIR', 'DATABASE_URL', 'NDIM_REQUIRE_DATABASE'):
        env.pop(name, None)  # the teacher journeys go to a throwaway data folder, never a real one
    return env


# ---------------------------------------------------------------- stages
def stage_dataset(ctx):
    a, data, log = ctx['args'], ctx['dir'] / 'data', ctx['dir'] / 'dataset.log'
    data.mkdir(exist_ok=True)
    py, env = a.engine_python, engine_env()
    run([py, HERE / 'make_dataset.py', '--journeys', a.journeys, '--seed', 1, '--out', data / 'train.jsonl'], log, env=env)
    run([py, HERE / 'make_dataset.py', '--tools', '--journeys', a.tools_journeys, '--seed', 3, '--out', data / 'tools.jsonl',
         '--schema-out', data / 'tools_schema.json'], log, env=env)
    run([py, HERE / 'make_replay.py', '--system-from', data / 'tools.jsonl', '--tools', data / 'tools_schema.json',
         '--model', ctx['base'], '--host', a.host, '--rounds', a.replay_rounds, '--out', data / 'replay.jsonl'], log, env=env)
    run([py, HERE / 'export_lessons.py', '--system-from', data / 'tools.jsonl', '--out', data / 'lessons.jsonl']
        + (['--lessons', a.lessons] if a.lessons else []), log, env=env)
    for path, extra in ((Path(a.heldout).expanduser(), ['--journeys', 24, '--seed', 99]),
                        (Path(a.tools_heldout).expanduser(), ['--tools', '--journeys', 10, '--seed', 98])):
        if not path.exists():  # built once, then fixed: every version is measured on the same questions
            run([py, HERE / 'make_dataset.py', '--heldout', '--out', path, *extra], log, env=env)
    files = [data / name for name in TRAIN_FILES]
    return {'sha256': sha256(*files), 'files': {f.name: kinds(f) for f in files},
            'lessons': sum(1 for _ in open(data / 'lessons.jsonl', encoding='utf-8')),
            'heldout_sha256': sha256(Path(a.heldout).expanduser()), 'tools_heldout_sha256': sha256(Path(a.tools_heldout).expanduser())}


def stage_train(ctx):
    a, data, out = ctx['args'], ctx['dir'] / 'data', ctx['dir'] / 'train'
    files = [data / name for name in TRAIN_FILES if (data / name).stat().st_size]
    cmd = [a.train_python, HERE / 'train_lora.py', '--data', *files, '--tools-schema', data / 'tools_schema.json',
           '--base', a.base_hf, '--lr', a.lr, '--max-len', a.max_len, '--out', out, '--merge', '--max-steps', a.max_steps]
    if a.max_examples:
        cmd += ['--max-examples', a.max_examples]
    unload_all(a.host)
    start = time.time()
    run(cmd, ctx['dir'] / 'train.log')
    info = json.loads((out / 'train_info.json').read_text())
    losses = [row['loss'] for row in info['log'] if 'loss' in row] or [row['train_loss'] for row in info['log'] if 'train_loss' in row]
    steps = max((row.get('step', 0) for row in info['log']), default=0)
    result = {'examples': info['examples'], 'steps': steps, 'final_loss': losses[-1] if losses else None,
              'minutes': round((time.time() - start) / 60, 1), 'max_steps': a.max_steps, 'lr': a.lr}
    if losses and losses[-1] < 0.01:
        result['warning'] = 'training loss near 0: the model may copy its examples (v1 did) and lose tool calling'
    return result


def stage_convert(ctx):
    a, gguf = ctx['args'], ctx['dir'] / 'model-f16.gguf'
    run([a.train_python, Path(a.llama_cpp) / 'convert_hf_to_gguf.py', ctx['dir'] / 'train' / 'merged', '--outtype', 'f16',
         '--outfile', gguf], ctx['dir'] / 'convert.log')
    return {'gguf': str(gguf), 'gb': round(gguf.stat().st_size / 1e9, 2)}


def stage_create(ctx):
    a, folder = ctx['args'], ctx['dir']
    template = ollama(a.host, '/api/show', {'model': ctx['base']})['modelfile']
    lines = [line for line in template.splitlines() if not line.startswith('FROM ')]
    while lines and (lines[0].startswith('#') or not lines[0].strip()):  # the generated header comment
        lines.pop(0)
    (folder / 'Modelfile').write_text('FROM ./model-f16.gguf\n' + '\n'.join(lines) + '\n', encoding='utf-8')
    env = dict(os.environ, OLLAMA_HOST=a.host)
    run([a.ollama_bin, 'create', ctx['model'], '-f', 'Modelfile'], folder / 'create.log', cwd=folder, env=env)
    digest = installed(a.host).get(ctx['model'])
    if not digest:
        raise SystemExit(f'{ctx["model"]} is not in the Ollama at {a.host} after create')
    if not a.keep_gguf:
        (folder / 'model-f16.gguf').unlink(missing_ok=True)  # Ollama keeps its own copy
    return {'model': ctx['model'], 'digest': digest}


def evaluate_model(ctx, model, digest, power):
    """Flat gate scores for one model, from the cache when this model and these held-out sets were scored before."""
    import evaluate
    a = ctx['args']
    key = f"{digest}|{ctx['heldout_key']}|bench={not a.no_bench}"
    cache_file = Path(a.work).expanduser() / 'eval_cache.json'
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    if key in cache:
        print(f'  {model}: cached scores', flush=True)
        return cache[key]
    print(f'  {model}: asking the held-out questions', flush=True)
    answers = evaluate.score(model, ctx['answer_rows'], a.host, power)
    tools = evaluate.tool_score(model, ctx['tool_rows'], a.host, ctx['tools_schema'])
    bench = None
    if not a.no_bench:
        out = ctx['dir'] / 'eval' / f"bench_{re.sub(r'[^A-Za-z0-9.-]', '_', model)}.json"
        out.unlink(missing_ok=True)
        run([sys.executable, ROOT / 'scripts' / 'local_ai_benchmark' / 'llm_bench.py', 'tasks', model], ctx['dir'] / 'bench.log',
            env=dict(os.environ, OLLAMA=a.host, BENCH_OUT=str(out)))
        bench = json.loads(out.read_text())[model]['tasks']
    entry = {'model': model, 'digest': digest, 'scores': gate.flatten(answers, tools, bench),
             'answers': {k: v for k, v in answers.items() if k != 'examples'}, 'examples': answers['examples'],
             'tools': tools, 'bench': bench}
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    cache[key] = entry
    cache_file.write_text(json.dumps(cache, indent=1, ensure_ascii=False))
    return entry


def heldout(ctx):
    """The held-out questions to ask (a stratified share with --eval-fraction) and a key naming them."""
    import evaluate
    a = ctx['args']
    fraction = a.eval_fraction
    evaluate.PER_KIND = {kind: max(2, round(n * fraction)) for kind, n in evaluate.PER_KIND.items()}
    ctx['answer_rows'] = evaluate.sample([json.loads(line) for line in open(Path(a.heldout).expanduser(), encoding='utf-8')])
    by_kind = {}
    for line in open(Path(a.tools_heldout).expanduser(), encoding='utf-8'):
        row = json.loads(line)
        by_kind.setdefault(row['kind'], []).append(row)
    ctx['tool_rows'] = [row for rows in by_kind.values() for row in rows[:max(2, round(len(rows) * fraction))]]
    ctx['tools_schema'] = json.loads((ctx['dir'] / 'data' / 'tools_schema.json').read_text())
    ctx['heldout_key'] = '|'.join([sha256(Path(a.heldout).expanduser())[:16], sha256(Path(a.tools_heldout).expanduser())[:16],
                                   sha256(ctx['dir'] / 'data' / 'tools_schema.json')[:16], f'fraction={fraction}'])


def stage_evaluate(ctx):
    import evaluate
    a = ctx['args']
    (ctx['dir'] / 'eval').mkdir(exist_ok=True)
    heldout(ctx)
    tags = installed(a.host)
    models = {'candidate': ctx['model'], 'base': ctx['base']}
    promoted = ctx['registry'].get('promoted')
    if promoted and promoted != ctx['model']:
        models['promoted'] = promoted
    power, out = evaluate.Power(), {'questions': {'answers': len(ctx['answer_rows']), 'tools': len(ctx['tool_rows'])},
                                    'fraction': a.eval_fraction}
    try:
        for role, model in models.items():
            if model not in tags:
                out[role] = {'model': model, 'missing': f'{model} is not installed in the Ollama at {a.host}'}
                print(f'  {role} {model}: not installed', flush=True)
                continue
            out[role] = evaluate_model(ctx, model, tags[model], power)
    finally:
        power.proc.terminate()
    (ctx['dir'] / 'eval' / 'scores.json').write_text(json.dumps(out, indent=1, ensure_ascii=False))
    return {role: value.get('scores') or value for role, value in out.items() if role in models} | {'questions': out['questions']}


def stage_gate(ctx):
    a, ev = ctx['args'], ctx['state']['stages']['evaluate']
    candidate, base, promoted = ev['candidate'], ev.get('base'), ev.get('promoted')
    if 'missing' in candidate:
        raise SystemExit(candidate['missing'])
    decision = gate.decide(candidate, None if promoted is None or 'missing' in promoted else promoted,
                           None if base is None or 'missing' in base else base, a.tolerance, a.overall_tolerance)
    if promoted and 'missing' in promoted:  # never promote past a model we could not measure
        decision['verdict'] = 'rejected'
        decision['reasons'].append(f"the promoted model could not be measured: {promoted['missing']}")
    if base and 'missing' in base:
        decision['notes'] = [f"base model not measured: {base['missing']}"]
    stages = ctx['state']['stages']
    entry = {'model': ctx['model'], 'version': a.version, 'verdict': decision['verdict'], 'reasons': decision['reasons'],
             'scores': candidate, 'base_scores': None if not base or 'missing' in base else base,
             'promoted_before': ctx['registry'].get('promoted'),
             'promoted_scores': None if not promoted or 'missing' in promoted else promoted,
             'dataset_sha256': stages['dataset']['sha256'], 'dataset': stages['dataset']['files'],
             'heldout_questions': ev['questions'], 'eval_fraction': a.eval_fraction, 'train': stages.get('train'),
             'digest': stages['create']['digest'], 'run_dir': str(ctx['dir'])}
    gate.record(a.registry, entry, promote=decision['verdict'] == 'promoted')
    if decision['verdict'] == 'rejected' and a.remove_rejected:
        with open(ctx['dir'] / 'create.log', 'a') as log:
            code = subprocess.call([a.ollama_bin, 'rm', ctx['model']], env=dict(os.environ, OLLAMA_HOST=a.host), stdout=log, stderr=log)
        decision['removed_from_ollama'] = code == 0
    return decision


# ---------------------------------------------------------------- report
def report(ctx):
    state, a = ctx['state'], ctx['args']
    stages = state['stages']
    lines = [f"# Fine-tune run {ctx['model']}", '', f"Updated {datetime.now().isoformat(timespec='seconds')}. Folder: `{ctx['dir']}`.", '',
             '| stage | finished | |', '|---|---|---|']
    for name in STAGES:
        done = stages.get(name)
        lines.append(f"| {name} | {done['finished_at'] if done else '-'} | {done.get('summary', '') if done else ''} |")
    if 'dataset' in stages:
        d = stages['dataset']
        lines += ['', f"Dataset sha256 `{d['sha256']}`; researcher-checked lessons: {d['lessons']}.", '']
        lines += [f"- {name}: {json.dumps(counts)}" for name, counts in d['files'].items()]
    if 'train' in stages:
        t = stages['train']
        lines += ['', f"Training: {t['examples']} examples, {t['steps']} steps, final loss {t['final_loss']}, {t['minutes']} min."
                  + (f" **{t['warning']}**" if t.get('warning') else '')]
    if 'evaluate' in stages:
        ev = stages['evaluate']
        roles = [r for r in ('base', 'promoted', 'candidate') if r in ev]
        keys = sorted({k for r in roles for k in ev[r] if k not in ('n', 'model', 'missing', 'seconds', 'joules')})
        lines += ['', f"Held-out questions: {ev['questions']} (fraction {a.eval_fraction}).", '',
                  '| item | ' + ' | '.join(roles) + ' |', '|---|' + '---|' * len(roles)]
        lines += [f'| {k} | ' + ' | '.join(str(ev[r].get(k, '-')) for r in roles) + ' |' for k in keys]
        lines += [f"- {r}: {ev[r]['missing']}" for r in roles if 'missing' in ev[r]]
    if 'gate' in stages:
        g = stages['gate']
        lines += ['', f"## Gate: {g['verdict'].upper()}", '',
                  f"Tolerance {g['tolerance']} (or one held-out item) per safety item; overall tool score may drop "
                  f"{g['overall_tolerance']}. Registry: `{a.registry}`.", '']
        lines += [f'- {reason}' for reason in g['reasons']] or ['- every safety item held and the overall tool score did not drop']
    (ctx['dir'] / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (ctx['dir'] / 'report.json').write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding='utf-8')


SUMMARY = {
    'dataset': lambda r: f"{sum(sum(c.values()) for c in r['files'].values())} examples, {r['lessons']} lessons",
    'train': lambda r: f"{r['steps']} steps, loss {r['final_loss']}",
    'convert': lambda r: f"{r['gb']} GB",
    'create': lambda r: r['model'],
    'evaluate': lambda r: f"tools.all candidate {r['candidate'].get('tools.all')}",
    'gate': lambda r: r['verdict'],
}


def main(argv=None):
    a = parse(argv)
    registry = gate.load_registry(a.registry)
    folder = Path(a.work).expanduser() / a.version
    folder.mkdir(parents=True, exist_ok=True)
    state_file = folder / 'run.json'
    state = json.loads(state_file.read_text()) if state_file.exists() else {'stages': {}}
    state['args'] = {k: v for k, v in vars(a).items() if k not in RESUME_FREE}
    ctx = {'args': a, 'dir': folder, 'state': state, 'registry': registry, 'base': registry.get('base', 'qwen3:1.7b'),
           'model': f"{registry.get('family', 'ndim-qwen3-1.7b')}:{a.version}"}
    state['model'] = ctx['model']
    first = STAGES.index(a.from_stage) if a.from_stage else 0
    last = STAGES.index(a.to_stage) if a.to_stage else len(STAGES) - 1
    if a.from_stage:
        for name in STAGES[first:]:
            state['stages'].pop(name, None)
    print(f"fine-tune pipeline: {ctx['model']} in {folder}", flush=True)
    try:
        for name in STAGES[first:last + 1]:
            if name in state['stages']:
                print(f'[{name}] done earlier, skipped', flush=True)
                continue
            print(f'[{name}]', flush=True)
            result = globals()[f'stage_{name}'](ctx)
            result['finished_at'] = datetime.now().isoformat(timespec='seconds')
            result['summary'] = SUMMARY[name](result)
            state['stages'][name] = result
            state_file.write_text(json.dumps(state, indent=1, ensure_ascii=False))
            print(f"[{name}] {result['summary']}", flush=True)
    finally:
        state_file.write_text(json.dumps(state, indent=1, ensure_ascii=False))
        report(ctx)
    print(f'report: {folder / "report.md"}', flush=True)
    return state


if __name__ == '__main__':
    main()
