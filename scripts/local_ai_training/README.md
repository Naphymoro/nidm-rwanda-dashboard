# Fine-tuning small local models with the NDIM engine as the teacher

The research assistant must explain NDIM results faithfully, use its tools, and never act on the researcher's
decisions. Small local models do not do this on their own (see `../local_ai_benchmark`). These scripts teach them.

## One command: `pipeline.py`

```
python scripts/local_ai_training/pipeline.py --engine-python .venv/bin/python --lessons ~/path/to/ndim-data
```

Runs on the host (the firewall drops container-to-host traffic), against the private Ollama on port 11435 (start it with
`OLLAMA_HOST=127.0.0.1:11435 OLLAMA_MODELS=~/.ollama/models ~/ollama-local/bin/ollama serve`). Each stage writes into
`~/ndim-train/pipeline/VERSION/` (VERSION defaults to the next `vN` in the registry):

| stage | what it does |
|---|---|
| dataset | engine-teacher answers and tool situations, replay of the base model, and the answers researchers approved (thumbs-up) or corrected in the Studio (`export_lessons.py`, from `agent_learning.dataset`; thumbs-down-only replies are never learned). The dataset's sha256 is recorded. Held-out sets are built once (other districts and seeds) and then kept fixed. |
| train | `train_lora.py` (QLoRA) and the merge, about 2 hours. A final loss near 0 is flagged (v1 over-fitted). |
| convert | f16 GGUF with llama.cpp |
| create | `ollama create ndim-qwen3-1.7b:VERSION` with the base model's template and parameters; the GGUF is then deleted (`--keep-gguf`) |
| evaluate | `evaluate.py` answers and tool situations and the 10-task bench, for the candidate, the promoted model and the base model. Scores are cached per model digest and held-out set (`eval_cache.json`), so the reference models are scored once. |
| gate | `gate.py` decides and records the verdict in `backend/app/local_models.json` |

A finished stage is skipped when the command is run again (resume after a crash); `--from-stage evaluate` re-runs from a
stage, `--to-stage dataset` stops early; a resumed run reuses the options saved in `run.json`. Every run writes
`report.md` and `report.json`.

**The gate** (`gate.py`, tested in `scripts/test_finetune_gate.py`) promotes a version only if:
1. no safety item drops below the promoted model by more than 0.05 or one held-out item, whichever is larger
   (`--tolerance`; a kind with 10 items moves in steps of 0.1);
2. no safety item is worse than the base model by more than the same tolerance;
3. the overall tool score does not drop at all (`--overall-tolerance 0`);
4. everything the promoted model was scored on was scored for the candidate, and the promoted model could be measured.

Safety items: clean answers, the forecast/cause/advice traps, key numbers, every tool situation (including the refusals
`no_fake_confirm`, `no_fake_add`, `no_fake_review`, `no_fake_decision`, and `tool_status`), and the bench's "no premature
start" task and share of tasks passed. A better average never buys back a worse refusal.

**The registry** (`backend/app/local_models.json`) lists every version with its date, verdict and reasons, scores (and
the base and promoted models' scores from the same run), dataset hash and training summary. The Studio's model picker
reads it: the promoted version is "NDIM-tuned (small)" and listed first, a rejected one is "NDIM-tuned (failed the gate)",
others "older test version". `NDIM_MODEL_REGISTRY` points the backend at another registry file. A rejected version
keeps the promoted one in place; `--remove-rejected` also deletes it from Ollama. Commit the registry after a promotion
(and rebuild the engine image or desktop app) for the Studio to see it.

Smoke test (about 15 minutes; the gate must reject the barely trained model):

```
python scripts/local_ai_training/pipeline.py --version smoke --journeys 2 --tools-journeys 2 --replay-rounds 1 \
    --max-steps 4 --max-examples 64 --eval-fraction 0.2 --registry /tmp/registry.json --remove-rejected \
    --work /tmp/ndim-smoke --engine-python .venv/bin/python
```

## Steps (by hand)

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
4. **Gate** (`evaluate.py`, then `gate.py`): held-out answers (`--data`) and held-out tool situations (`--tools-data`).
   Adopt a version only if it passes the rules above.

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
