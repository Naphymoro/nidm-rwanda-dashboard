"""Replay examples: everyday Studio requests answered by the original model, so fine-tuning keeps its general abilities.

A fine-tune trained only on stage explanations turned the model into a copier: asked anything, it pasted text from
its instructions. Mixing in the original model's own answers to ordinary requests (rewriting, summarising given text,
explaining general methods, conversation) keeps that behaviour. Low-risk tasks only: the replay must not teach facts
the original model might have invented.

    python make_replay.py --system-from tools.jsonl --tools tools_schema.json --model qwen3:1.7b --out replay.jsonl
"""
import argparse
import json
import random
import re
import urllib.request

NOTE = ('Households in the sector say the improved stoves save charcoal and they trust the health worker who showed '
        'them, but the price is too high and some neighbours heard a rumour that the smoke makes food taste bad.')
PROMPTS = [
    'Rewrite this field note in simpler English: "{note}"', 'Summarise this note in one sentence: "{note}"',
    'Turn this note into three bullet points: "{note}"', 'Suggest a short title for this field note: "{note}"',
    'Fix the grammar: "the household say they trusts the health worker but price high"',
    'Write a polite two-sentence email thanking a cooperative leader for hosting our focus group.',
    'Write a short consent reminder for field interviewers, in plain language.',
    'Give me a checklist for writing a good field note: what should each note include?',
    'What is the difference between an interview and a focus group, briefly?',
    'Explain in two sentences what an SIR model is in epidemiology.',
    'In general terms, what is a sensitivity analysis?', 'What does "uncalibrated model" mean, in plain words?',
    'What is pre-bunking, in one or two sentences?', 'Explain what an echo chamber is on social media, briefly.',
    'How can I describe uncertainty to a district officer without jargon?', 'Thank you, that helps.', 'Hello!',
    'What can you help me with in this tool?', 'Make this sentence more neutral: "The stove is obviously the best choice."',
    'List three open questions I could ask households about cooking habits.',
    'How should I store field notes safely?', 'What is a keyword heuristic, in plain words?',
    'Write a one-paragraph plain-language summary of why models are not forecasts.',
    'Convert 0.35 to a percentage and explain what it means as a share of households.',
    'What is the difference between correlation and causation? Keep it short.',
    'Suggest a neutral way to ask about rumours without spreading them further.',
]


def ask(host, model, system, tools, prompt):
    body = {'model': model, 'stream': False, 'think': False, 'tools': tools, 'options': {'temperature': 0.3, 'num_ctx': 8192, 'num_predict': 350},
            'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}]}
    req = urllib.request.Request(host + '/api/chat', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=600) as response:
        return json.loads(response.read())['message']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--system-from', required=True, help='tool examples file; a no-journey Studio system prompt is taken from it')
    parser.add_argument('--tools', required=True)
    parser.add_argument('--model', default='qwen3:1.7b')
    parser.add_argument('--host', default='http://127.0.0.1:11435')
    parser.add_argument('--rounds', type=int, default=6)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    systems = [json.loads(line)['messages'][0]['content'] for line in open(args.system_from, encoding='utf-8')
               if json.loads(line)['kind'] == 'tool_propose']
    tools = json.load(open(args.tools, encoding='utf-8'))
    rng, rows = random.Random(4), []
    for round_ in range(args.rounds):
        for template in PROMPTS:
            prompt = template.format(note=NOTE)
            message = ask(args.host, args.model, rng.choice(systems), tools, prompt)
            text = re.sub(r'<think>.*?</think>', '', message.get('content') or '', flags=re.S).strip()
            if message.get('tool_calls') or not text:
                continue  # keep plain replies; tool behaviour comes from the tool examples
            rows.append({'messages': [{'role': 'system', 'content': rng.choice(systems)}, {'role': 'user', 'content': prompt},
                                      {'role': 'assistant', 'content': text}], 'kind': 'replay'})
    with open(args.out, 'w', encoding='utf-8') as out:
        out.writelines(json.dumps(row, ensure_ascii=False) + '\n' for row in rows)
    print(f'{len(rows)} replay examples -> {args.out}')


if __name__ == '__main__':
    main()
