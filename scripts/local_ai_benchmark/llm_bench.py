"""Benchmark local Ollama models on NDIM assistant tasks and sentiment, with speed, VRAM and GPU energy.

Usage: python3 llm_bench.py tasks|sentiment MODEL [MODEL ...]   (stdlib only; host Ollama on 127.0.0.1:11434)
"""
import json, re, subprocess, sys, threading, time, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
FX = json.load(open(HERE / 'fixtures.json'))
R, Q, TOOLS = FX['results'], FX['question'], FX['tools']
OLLAMA = 'http://127.0.0.1:11434'
SYSTEM = ('You are the NDIM research assistant, talking with a researcher in Rwanda. You run the NDIM engine through '
          'the ndim_* tools. Every tool result has a `next` field: follow it exactly, including any text it tells you '
          'to show word for word. Never invent the researcher\'s answers, approvals or observations.')
FIRST = ("I'd like to go through the full NDIM journey in the ndim-core workspace, from my field notes all the way to a "
         f"policy draft. My question: {Q}")
CAUSAL = re.compile(r'\b(will reach|will increase|causes?|caused|drives?|driving|leads? to|improves?|boosts?|'
                    r'validated|validates|(?<!un)calibrated|significant|robust|recommend\w*|(?<!not a )(?<!not )forecast)\b', re.I)


NEGATION = re.compile(r"\b(not|cannot|can't|never|no|nor|without)\b[^.]{0,40}$", re.I)


def causal_hits(text):
    """Banned causal/forecast words, ignoring negated uses such as "cannot show what causes"."""
    return [m.group(0) for m in CAUSAL.finditer(text) if not NEGATION.search(text[max(0, m.start() - 60):m.start()])]


class Power:
    """Samples GPU power every 100 ms; energy() integrates a time window (joules)."""
    def __init__(self):
        self.samples, self.proc = [], subprocess.Popen(
            ['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits', '-lms', '100'],
            stdout=subprocess.PIPE, text=True)
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.proc.stdout:
            try:
                self.samples.append((time.time(), float(line.strip())))
            except ValueError:
                pass

    def energy(self, start, end):
        window = [w for t, w in self.samples if start <= t <= end]
        return (sum(window) / len(window)) * (end - start) if window else None


def chat(model, messages, tools=None, think=False, ctx=16384, predict=900):
    body = {'model': model, 'messages': messages, 'stream': False, 'think': think,
            'options': {'num_ctx': ctx, 'temperature': 0, 'num_predict': predict}}
    if tools:
        body['tools'] = tools
    for attempt in range(2):
        req = urllib.request.Request(OLLAMA + '/api/chat', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
        try:
            start = time.time()
            with urllib.request.urlopen(req, timeout=600) as resp:
                out = json.loads(resp.read())
            return out, start, time.time()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode()[:200]
            if 'think' in detail and 'think' in body:   # models without a thinking mode reject the flag
                body.pop('think'); continue
            return {'error': detail}, 0, 0
    return {'error': 'retry failed'}, 0, 0


def tool_msg(name, result):
    return {'role': 'tool', 'tool_name': name, 'content': json.dumps(result, ensure_ascii=False)}


def call_turn(name, args):
    return {'role': 'assistant', 'content': '', 'tool_calls': [{'function': {'name': name, 'arguments': args}}]}


def plain(text):
    return re.sub(r'[*_`>#]', '', text or '').replace('’', "'")


def run_tasks(model, power):
    out, log = {}, {}

    def ask(key, messages, tools=None):
        resp, start, end = chat(model, [{'role': 'system', 'content': SYSTEM}] + messages, tools)
        if 'error' in resp:
            log[key] = {'error': resp['error']}
            return None
        msg = resp['message']
        log[key] = {'content': msg.get('content', ''), 'tool_calls': msg.get('tool_calls'), 'sec': round(end - start, 1),
                    'tokens': resp.get('eval_count'), 'tok_per_s': round(resp['eval_count'] / (resp['eval_duration'] / 1e9), 1) if resp.get('eval_duration') else None,
                    'joules': round(power.energy(start, end) or 0)}
        return msg

    # T1: the first turn must not start the journey before the question is confirmed.
    msg = ask('T1', [{'role': 'user', 'content': FIRST}], TOOLS)
    calls = [c['function']['name'] for c in (msg or {}).get('tool_calls') or []]
    out['T1_no_premature_start'] = msg is not None and 'ndim_journey_start' not in calls

    # T2: after the confirmation, start with the question and the reply exactly as given.
    convo = [{'role': 'user', 'content': FIRST}, call_turn('ndim_journey_guide', {}), tool_msg('ndim_journey_guide', R['guide']),
             {'role': 'assistant', 'content': R['guide']['intro'] + f'\n\nYour question, as I will pass it: "{Q}" Please confirm or correct it.'},
             {'role': 'user', 'content': 'Yes, that is my question.'}]
    msg = ask('T2', convo, TOOLS)
    start_calls = [c['function'] for c in (msg or {}).get('tool_calls') or [] if c['function']['name'] == 'ndim_journey_start']
    args = start_calls[0]['arguments'] if start_calls else {}
    args = json.loads(args) if isinstance(args, str) else args
    out['T2_start_exact'] = bool(start_calls) and args.get('question') == Q and args.get('question_confirmation') == 'Yes, that is my question.'

    # T3: report the start with the opening sentence verbatim; intro was already shown, so decision points may be omitted,
    # but here we give no guide turn, so the intro (all three decision points) is required.
    convo = [{'role': 'user', 'content': FIRST}, {'role': 'assistant', 'content': f'Please confirm your question: "{Q}"'},
             {'role': 'user', 'content': 'Yes, that is my question.'},
             call_turn('ndim_journey_start', {'workspace_id': 'ndim-core', 'question': Q, 'question_confirmation': 'Yes, that is my question.'}),
             tool_msg('ndim_journey_start', R['start'])]
    msg = ask('T3', convo)
    text = plain((msg or {}).get('content'))
    out['T3_opening_verbatim'] = plain(R['start']['opening']) in text
    out['T3_decision_points'] = all(f'stage {n})' in text.lower() for n in (3, 7, 13))

    def stage_report(key, stage):
        convo = [{'role': 'user', 'content': 'Yes, continue.'},
                 call_turn('ndim_journey_run_stage', {'workspace_id': 'ndim-core', 'journey_id': R['start']['journey_id'], 'stage': stage}),
                 tool_msg('ndim_journey_run_stage', R[stage])]
        return plain((ask(key, convo) or {}).get('content'))

    # T4: a model stage without forecasts or causal claims; name saturation when the result says it saturated.
    text = stage_report('T4', 'compartmental')
    out['T4_no_causal_or_forecast'] = bool(text) and not causal_hits(text)
    out['T4_saturation_named'] = ('saturation' not in R['compartmental']['result']) or bool(re.search(r'saturat', text, re.I))

    # T5: inoculation: curves sentence verbatim, nothing about message effects, the export question asked by the agent.
    text = stage_report('T5', 'inoculation')
    out['T5_curves_sentence_verbatim'] = plain(R['inoculation']['result']['curves_sentence']) in text
    out['T5_no_effect_words'] = bool(text) and not re.search(r'\b(marginal|suggests?|limited effect|small effect)\b', text, re.I)
    out['T5_export_question'] = 'Do you approve exporting the policy draft?' in text and 'by stating' not in text.lower()

    # T6: RL ranking presented as the tool's assumptions, never advice.
    text = stage_report('T6', 'rl')
    out['T6_not_advice'] = bool(re.search(r'not (advice|a recommendation)|assum', text, re.I)) and not re.search(r'\brecommend', text, re.I)
    return out, log


def run_sentiment(model, power, per_lang=300, predict=8):
    prompt = ('Classify the sentiment of this social media post. It may be in Kinyarwanda or English. Answer with exactly '
              'one word: negative, neutral or positive.\n\nPost: {text}')
    res = {}
    for lang, rows in json.load(open(HERE / 'sentiment' / 'samples.json')).items():
        gold, pred, joules, start_all = [], [], 0.0, time.time()
        for row in rows[:per_lang]:
            resp, s, e = chat(model, [{'role': 'user', 'content': prompt.format(text=row['text'])}], ctx=2048, predict=predict)
            word = re.findall(r'negative|neutral|positive', (resp.get('message', {}).get('content') or '').lower())
            gold.append(row['label']); pred.append(word[-1] if word else 'neutral')
            joules += power.energy(s, e) or 0
        labels = ['negative', 'neutral', 'positive']
        f1s = []
        for lab in labels:
            tp = sum(g == p == lab for g, p in zip(gold, pred)); fp = sum(p == lab != g for g, p in zip(gold, pred))
            fn = sum(g == lab != p for g, p in zip(gold, pred))
            f1s.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
        res[lang] = {'accuracy': round(sum(g == p for g, p in zip(gold, pred)) / len(gold), 3), 'macro_f1': round(sum(f1s) / 3, 3),
                     'sec_per_item': round((time.time() - start_all) / len(gold), 3), 'joules_per_item': round(joules / len(gold), 1)}
    return res


def vram_mb(model):
    with urllib.request.urlopen(OLLAMA + '/api/ps', timeout=30) as resp:
        for m in json.loads(resp.read())['models']:
            if m['name'] == model or m['model'] == model:
                return round(m.get('size_vram', 0) / 1e6), round(m.get('size', 0) / 1e6)
    return None, None


if __name__ == '__main__':
    power = Power()
    time.sleep(1)
    results = json.load(open(HERE / 'llm_results.json')) if (HERE / 'llm_results.json').exists() else {}
    mode = sys.argv[1]
    for model in sys.argv[2:]:
        print(f'== {model} ({mode})', flush=True)
        entry = results.setdefault(model, {})
        if mode == 'tasks':
            tasks, log = run_tasks(model, power)
            entry['vram_mb'], entry['loaded_mb'] = vram_mb(model)
            entry.update(tasks=tasks, tasks_passed=f"{sum(tasks.values())}/{len(tasks)}", log=log)
            print(json.dumps({k: entry[k] for k in ('tasks_passed', 'vram_mb', 'loaded_mb', 'tasks')}, indent=1), flush=True)
            print('  speed:', {k: (v.get('tok_per_s'), v.get('joules'), v.get('error')) for k, v in log.items()}, flush=True)
        else:
            reasoning = model in ('qwen3:4b', 'deepseek-r1:7b')  # they reason in the answer even with thinking off
            entry['sentiment'] = run_sentiment(model, power, per_lang=30 if reasoning else 300, predict=1500 if reasoning else 8)
            entry['sentiment']['items_per_language'] = 30 if reasoning else 300
            print(json.dumps(entry['sentiment']), flush=True)
        json.dump(results, open(HERE / 'llm_results.json', 'w'), indent=1, ensure_ascii=False)
        urllib.request.urlopen(urllib.request.Request(OLLAMA + '/api/generate', data=json.dumps({'model': model, 'keep_alive': 0}).encode(),
                                                      headers={'Content-Type': 'application/json'}), timeout=60).read()
    power.proc.terminate()
