"""Sentiment from a small classifier trained on African-language tweets, when it is installed; keywords otherwise.

The engine's English keyword heuristic labelled every Kinyarwanda tweet neutral (33% accuracy on 300 held-out AfriSenti
tweets). The AfroXLMR AfriSenti classifier, exported to 8-bit ONNX by scripts/local_ai_training/export_sentiment.py,
scored 74.7% on the same Kinyarwanda tweets and 67.3% on English ones, at about 0.02 s per text on a CPU, with no
PyTorch. It reads tweets, not field notes: check it against your own labelled notes before relying on it.

The model folder (model.onnx, tokenizer.json, labels.json, card.json) is found at NDIM_SENTIMENT_MODEL or
<data folder>/models/sentiment. Without it, or without onnxruntime and tokenizers, sentiment stays the keyword score.
"""
import json
import logging
import os
import threading
from pathlib import Path

from .storage import app_paths

log = logging.getLogger(__name__)
METHOD = 'AfroXLMR AfriSenti classifier (8-bit ONNX)'
_lock = threading.Lock()
_model = {}  # folder -> (session, tokenizer, labels, card) or None when it could not load


def folder():
    configured = os.getenv('NDIM_SENTIMENT_MODEL')
    return Path(configured) if configured else Path(app_paths()['data']) / 'models' / 'sentiment'


def _load():
    path = folder()
    with _lock:
        if str(path) in _model:
            return _model[str(path)]
        loaded = None
        if (path / 'model.onnx').is_file():
            try:
                import onnxruntime
                from tokenizers import Tokenizer
                tokenizer = Tokenizer.from_file(str(path / 'tokenizer.json'))
                card = json.loads((path / 'card.json').read_text()) if (path / 'card.json').is_file() else {}
                tokenizer.enable_truncation(card.get('max_tokens', 128))
                options = onnxruntime.SessionOptions()
                options.intra_op_num_threads = 2  # small and steady: the engine shares the machine
                session = onnxruntime.InferenceSession(str(path / 'model.onnx'), options, providers=['CPUExecutionProvider'])
                loaded = (session, tokenizer, json.loads((path / 'labels.json').read_text()), card)
            except Exception as exc:  # a broken or partial download must never stop the engine
                log.warning('Sentiment classifier at %s could not load (%s); using keywords', path, exc)
        _model[str(path)] = loaded
        return loaded


def status():
    loaded = _load()
    if not loaded:
        return {'available': False, 'method': 'English keyword heuristic', 'folder': str(folder())}
    card = loaded[3]
    return {'available': True, 'method': METHOD, 'source': card.get('source'), 'license': card.get('license'),
            'evaluation': card.get('evaluation')}


def classify(text):
    """{'label', 'probabilities', 'score'} for one text, score = P(positive) - P(negative) in [-1, 1]; None without a model."""
    loaded = _load()
    if not loaded or not (text or '').strip():
        return None
    import numpy as np
    session, tokenizer, labels, _ = loaded
    encoding = tokenizer.encode(text)
    logits = session.run(None, {'input_ids': np.array([encoding.ids], dtype=np.int64),
                                'attention_mask': np.array([encoding.attention_mask], dtype=np.int64)})[0][0]
    probabilities = np.exp(logits - logits.max())
    probabilities = probabilities / probabilities.sum()
    by_label = {label: round(float(p), 4) for label, p in zip(labels, probabilities)}
    return {'label': labels[int(probabilities.argmax())], 'probabilities': by_label,
            'score': round(by_label.get('positive', 0.0) - by_label.get('negative', 0.0), 4)}
