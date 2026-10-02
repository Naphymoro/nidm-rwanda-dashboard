# Fine-tuning small local models with the NDIM engine as the teacher

The research assistant must explain NDIM results faithfully, use its tools, and never act on the researcher's
decisions. Small local models do not do this on their own (see `../local_ai_benchmark`). These scripts teach them.

## Steps

1. **Data** (engine image or any environment with the backend's dependencies):
   - `make_dataset.py --journeys 120 --out train.jsonl --seed 1`: practice journeys on synthetic field notes; every
     finished stage becomes questions (explain, limits, and the forecast, cause and advice traps) answered with the
     engine's own text, under the Studio's real system prompt. Every answer must pass `agent_checks`.
   - `make_dataset.py --tools --journeys 60 --out tools.jsonl --seed 3`: Studio situations where the right reply is a
     tool call, and the ones where it is the researcher's decision (the reply points to the card).
   - `make_replay.py ...`: everyday requests answered by the original model, so the fine-tune keeps its abilities.
   - Held-out sets use other districts and seeds (`--heldout`).
2. **Train** (one GPU; QLoRA): `train_lora.py --data train.jsonl tools.jsonl replay.jsonl --tools-schema
   tools_schema.json --lr 1e-4 --max-len 4096 --out runs/NAME --merge`. About 2 hours for Qwen3-1.7B on an RTX 2000 Ada.
3. **Import into Ollama**: Ollama 0.35 imports safetensors only with its MLX runtime. Convert instead:
   `python llama.cpp/convert_hf_to_gguf.py runs/NAME/merged --outtype f16 --outfile NAME.gguf`, then `ollama create`
   with `FROM ./NAME.gguf` and the base model's TEMPLATE and PARAMETER lines (`ollama show qwen3:1.7b --modelfile`).
4. **Gate** (`evaluate.py`): held-out answers (`--data`) and held-out tool situations (`--tools-data`). Adopt a
   version only if it is at least as good as the original model on every safety item.

## Results so far (Qwen3-1.7B; held-out journeys in districts never seen in training)

| | original | v1 | v2 | v3 |
|---|---|---|---|---|
| answers with no invented numbers or claim words | 0.84 | 1.00 | 0.97 | 0.98 |
| forecast / cause / advice traps | 0.45 | 1.00 | 0.88 | 0.73 |
| key numbers stated | 0.36 | 1.00 | 1.00 | 0.97 |
| tool situations, all (v3 set) | 0.23 | – | 0.53 | 0.81 |
| refuses to fake: confirm / add / review / twin-export (v3 set) | 0 / 0 / 0 / 0 | – | 0 / 0 / 0 / 0.47 | 0.4 / 0.5 / 0.7 / 0.68 |

- v1 (stage answers only) became a copier and stopped calling tools.
- v2 added tool examples and replay; it learned "yes means act" (420 run examples against 60-120 refusals).
- v3 balanced refusals with runs and added natural "what's next" answers. In the Studio it proposed, filled the form
  and ran the requested stages correctly; it still pads tool calls with unused arguments and extracts sources poorly.

The card's buttons, not the model, make every decision, so a wrong attempt fails harmlessly.
