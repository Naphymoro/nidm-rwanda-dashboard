# Models the engine can use

`sentiment/`: the AfriSenti sentiment classifier (AfroXLMR, Apache-2.0) as 8-bit ONNX, about 560 MB, so not in git.
Make it with `scripts/local_ai_training/export_sentiment.py --out models/sentiment` (needs PyTorch and transformers
once), or copy an exported folder here. The engine image copies this folder and sets `NDIM_SENTIMENT_MODEL`; without
the files the engine reads sentiment with English keywords, as before. Accuracy and limits: `sentiment/card.json` and
`backend/app/sentiment.py`.
