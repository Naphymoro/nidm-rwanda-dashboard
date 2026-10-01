"""Sentiment benchmark: engine keyword heuristic vs small classifiers, Kinyarwanda (AfriSenti) and English (tweet_eval).

Runs in the NDIM engine image (CPU). Writes samples.json (shared with the LLM benchmark) and classifiers.json.
"""
import json, random, sys, time
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score

MODE = sys.argv[1]  # "classify": clean container (samples + classifiers); "keyword": engine image (needs /app)

D = '/data'
LABELS = ['negative', 'neutral', 'positive']
torch.set_num_threads(8)


def load():
    kin = {s: pd.read_csv(f'{D}/kin_{s}.tsv', sep='\t', quoting=3).rename(columns={'tweet': 'text'}) for s in ('dev', 'test')}
    if MODE == 'classify':  # the engine image has no parquet reader: leave TSV copies for the keyword run
        for s, f in (('dev', 'val'), ('test', 'test')):
            df = pd.read_parquet(f'{D}/en_{f}.parquet')
            df['label'] = df['label'].map(dict(enumerate(LABELS)))
            df.to_csv(f'{D}/en_{s}.tsv', sep='\t', index=False)
    en = {s: pd.read_csv(f'{D}/en_{s}.tsv', sep='\t', quoting=3, keep_default_na=False) for s in ('dev', 'test')}
    return {'kin': kin, 'en': en}


def sample(df, n=300, seed=7):
    """Stratified, fixed sample so every method (and the LLM benchmark) sees the same items."""
    rng = random.Random(seed)
    rows = []
    for label in LABELS:
        part = df[df.label == label].to_dict('records')
        rng.shuffle(part)
        rows += part[:n // 3]
    rng.shuffle(rows)
    return [{'text': r['text'], 'label': r['label']} for r in rows]


def keyword_scores(texts, lang):
    sys.path.insert(0, '/app')
    from app.encoding import encode_rule_based
    from app.schemas import NarrativeMetadata, NarrativeRecord
    meta = NarrativeMetadata(source_type='field_note', language=lang)
    return [encode_rule_based(NarrativeRecord(narrative_id=str(i), text=t, metadata=meta)).sentiment or 0.0
            for i, t in enumerate(texts)]


def tune_thresholds(scores, gold):
    """Pick the neg/pos cut-offs on dev that maximise macro-F1 (fair to the heuristic)."""
    best = (-1, 0, 0)
    grid = sorted(set(round(s, 3) for s in scores)) or [0.0]
    for lo in grid:
        for hi in grid:
            if hi < lo:
                continue
            pred = ['negative' if s < lo else 'positive' if s > hi else 'neutral' for s in scores]
            f1 = f1_score(gold, pred, average='macro')
            if f1 > best[0]:
                best = (f1, lo, hi)
    return best[1], best[2]


def classify(model_id, texts):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id).eval()
    names = [model.config.id2label[i].lower() for i in range(model.config.num_labels)]
    out, start = [], time.time()
    with torch.no_grad():
        for i in range(0, len(texts), 16):
            batch = tok(texts[i:i + 16], padding=True, truncation=True, max_length=128, return_tensors='pt')
            out += [names[k] for k in model(**batch).logits.argmax(-1).tolist()]
    params = sum(p.numel() for p in model.parameters())
    return out, (time.time() - start) / len(texts), params, names


def score(gold, pred):
    return {'accuracy': round(accuracy_score(gold, pred), 3), 'macro_f1': round(f1_score(gold, pred, average='macro'), 3)}


data = load()
if MODE == 'classify':
    samples = {lang: sample(data[lang]['test']) for lang in data}
    json.dump(samples, open(f'{D}/samples.json', 'w'), ensure_ascii=False)
else:
    samples = json.load(open(f'{D}/samples.json'))
results = {}
for lang in data:
    texts, gold = [r['text'] for r in samples[lang]], [r['label'] for r in samples[lang]]
    dev = data[lang]['dev']
    if MODE == 'classify':
        for model_id in ('Davlan/afrisenti-twitter-sentiment-afroxlmr-large', 'cardiffnlp/twitter-xlm-roberta-base-sentiment'):
            pred, sec, params, names = classify(model_id, texts)
            results[f'{lang}/{model_id}'] = score(gold, pred) | {'sec_per_item_cpu': round(sec, 4), 'params_m': round(params / 1e6), 'labels': names}
            print(lang, model_id, results[f'{lang}/{model_id}'], flush=True)
        continue
    lo, hi = tune_thresholds(keyword_scores(dev.text.tolist(), lang), dev.label.tolist())
    start = time.time()
    scores = keyword_scores(texts, lang)
    pred = ['negative' if s < lo else 'positive' if s > hi else 'neutral' for s in scores]
    results[f'{lang}/keyword'] = score(gold, pred) | {'sec_per_item': round((time.time() - start) / len(texts), 5),
                                                      'thresholds': [lo, hi], 'neutral_share': round(pred.count('neutral') / len(pred), 2)}
    print(lang, 'keyword', results[f'{lang}/keyword'], flush=True)
json.dump(results, open(f'{D}/{MODE}.json', 'w'), indent=1)
