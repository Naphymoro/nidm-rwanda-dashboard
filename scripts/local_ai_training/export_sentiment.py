"""Export the AfriSenti sentiment classifier as a small ONNX model the engine runs without PyTorch or transformers.

Source: Davlan/afrisenti-twitter-sentiment-afroxlmr-large (Apache-2.0), AfroXLMR fine-tuned on AfriSenti, which includes
Kinyarwanda. On 300 held-out Kinyarwanda tweets it scored 74% against 33% for the engine's English keyword heuristic
(scripts/local_ai_benchmark). Dynamic 8-bit quantization makes it about a quarter of the size; this script measures
what that costs, with the engine's own runtime (onnxruntime + tokenizers), before anything ships.

    python export_sentiment.py --samples samples.json --out models/sentiment-afroxlmr-int8

The output folder (model.onnx, tokenizer.json, labels.json, card.json) is what the engine loads from
NDIM_SENTIMENT_MODEL or <data folder>/models/sentiment.
"""
import argparse
import json
import shutil
import tempfile
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
from onnxruntime.quantization import QuantType, quantize_dynamic
from sklearn.metrics import accuracy_score, f1_score
from tokenizers import Tokenizer
from transformers import AutoModelForSequenceClassification, AutoTokenizer

SOURCE = 'Davlan/afrisenti-twitter-sentiment-afroxlmr-large'
MAX_TOKENS = 128


class Wrapped(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask):
        return self.model(input_ids=input_ids, attention_mask=attention_mask).logits


def run_onnx(folder, texts):
    """Exactly what the engine does (backend/app/sentiment.py): tokenizers + onnxruntime, batch of one."""
    tokenizer = Tokenizer.from_file(str(folder / 'tokenizer.json'))
    tokenizer.enable_truncation(MAX_TOKENS)
    session = ort.InferenceSession(str(folder / 'model.onnx'), providers=['CPUExecutionProvider'])
    labels = json.loads((folder / 'labels.json').read_text())
    out, start = [], time.time()
    for text in texts:
        encoding = tokenizer.encode(text)
        feeds = {'input_ids': np.array([encoding.ids], dtype=np.int64),
                 'attention_mask': np.array([encoding.attention_mask], dtype=np.int64)}
        out.append(labels[int(session.run(None, feeds)[0][0].argmax())])
    return out, (time.time() - start) / len(texts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', required=True, help='samples.json from scripts/local_ai_benchmark')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    hf_tokenizer = AutoTokenizer.from_pretrained(SOURCE)
    model = AutoModelForSequenceClassification.from_pretrained(SOURCE).eval()
    labels = [model.config.id2label[i].lower() for i in range(model.config.num_labels)]

    with tempfile.TemporaryDirectory() as tmp:
        full = Path(tmp) / 'full.onnx'  # over 2 GB: weights go to an external data file next to it
        sample = hf_tokenizer(['Murakoze cyane'], return_tensors='pt')
        torch.onnx.export(Wrapped(model), (sample['input_ids'], sample['attention_mask']), str(full),
                          input_names=['input_ids', 'attention_mask'], output_names=['logits'], opset_version=17,
                          dynamic_axes={'input_ids': {0: 'batch', 1: 'tokens'}, 'attention_mask': {0: 'batch', 1: 'tokens'},
                                        'logits': {0: 'batch'}}, external_data=True, dynamo=False)
        quantize_dynamic(str(full), str(out / 'model.onnx'), weight_type=QuantType.QInt8)
    hf_tokenizer.backend_tokenizer.save(str(out / 'tokenizer.json'))
    (out / 'labels.json').write_text(json.dumps(labels))

    samples = json.load(open(args.samples, encoding='utf-8'))
    card = {'source': SOURCE, 'license': 'Apache-2.0', 'quantization': 'dynamic int8 (onnxruntime)', 'max_tokens': MAX_TOKENS,
            'labels': labels, 'size_mb': round((out / 'model.onnx').stat().st_size / 1e6), 'evaluation': {}}
    for lang, rows in samples.items():
        texts, gold = [r['text'] for r in rows], [r['label'] for r in rows]
        pred, seconds = run_onnx(out, texts)
        with torch.no_grad():
            reference = [labels[int(model(**hf_tokenizer(t, return_tensors='pt', truncation=True, max_length=MAX_TOKENS)).logits.argmax())]
                         for t in texts]
        card['evaluation'][lang] = {
            'items': len(rows), 'int8_accuracy': round(accuracy_score(gold, pred), 3),
            'int8_macro_f1': round(f1_score(gold, pred, average='macro'), 3),
            'full_accuracy': round(accuracy_score(gold, reference), 3), 'agreement_with_full': round(accuracy_score(reference, pred), 3),
            'int8_seconds_per_item': round(seconds, 4)}
        print(lang, card['evaluation'][lang], flush=True)
    (out / 'card.json').write_text(json.dumps(card, indent=1))
    print('exported', out, f"{card['size_mb']} MB", flush=True)


if __name__ == '__main__':
    main()
