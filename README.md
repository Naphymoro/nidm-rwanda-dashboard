# NDIM: Narrative Diffusion and Inoculation Model

NDIM turns field notes (interviews, focus groups, stories) into **illustrative adoption scenarios, prebunking drafts and
a policy draft**, with every decision left to the researcher, a full audit trail, and the math shown step by step.
It was built for clean cooking in Rwanda and now ships examples for **vaccines, AI in the classroom and the just
transition**.

## Live

| | Link |
|---|---|
| **Research Studio** (start here) | https://nidm-engine.pages.dev/studio |
| Engine API (health check) | https://ndim-engine.couma.workers.dev/health |
| Field manual | https://nidm-engine.pages.dev/manual/ |
| Learning Academy (curriculum) | https://nidm-engine.pages.dev/academy/ |

Hosted on Cloudflare: static pages on Cloudflare Pages, the engine in a Cloudflare Container behind a Worker, data in
D1, and the research assistant on Workers AI. After 30 idle minutes the engine sleeps; the first request then takes
about 20 seconds.

**Start with the guided tour** (welcome screen, or *How it works* → *Start the guided tour*): it walks the whole
journey with Back and Next, on synthetic data or your own notes.

## What it does

- **The 13-stage journey**: field notes → gate (metadata, personal data, injection checks) → your accept/reject
  decisions → keyword encoding → population model → household network model → digital twin from your field numbers →
  Bayesian signal update → action ranking → regional analysis and knowledge graph → inoculation lab (pre-bunk,
  refutation, counter-message drafts) → policy draft with an evidence grade. Decisions are buttons only you can press.
- **Guided tour**: a coach above the chat says what each step does, what to click, and unlocks Next when it is done.
  Eight synthetic datasets (four topics × simple and thought-provoking), or your own notes typed, pasted or uploaded as
  CSV (up to 50; author columns are never read).
- **How it works**: every step's model in symbols, its derivation, the values NDIM uses, and a worked example the
  engine computes. Equations render with KaTeX in the panel, the library, the manual and the assistant's replies.
- **Research assistant** that teaches: answers from the guide, the manual and the curriculum, opens the journey card,
  never makes your decisions, and replies in your language. On the hosted demo it runs **GLM 5.3 Flash on Cloudflare
  Workers AI** within a free daily allowance (9,000 Neurons a day, 40 messages per visitor). Visitors can **use their own
  key** (OpenRouter, OpenAI, Anthropic, DeepSeek): it stays in their browser and is used for their reply only.
- **Sensitivity analysis**: Sobol indices show which inputs and which of NDIM's own assumptions drive a result.
- **Robustness and messenger seeding**: the household model is re-run on seven assumed network shapes, and campaign
  recruiting strategies (random, best connected, bridges) are compared.
- **Kinyarwanda**: notes in Kinyarwanda need an English translation checked by a person; sentiment reads the original
  with an AfriSenti-trained classifier.

## The model, honestly

NDIM's results are **illustrative and uncalibrated**: scenarios, not forecasts.

- Notes are scored by **counting words** from fixed lists (with negation and topic word lists). That is not
  understanding: "many buyers believe the rumour" still counts *believe* as trust.
- The population model (S/M/T/I/R) has a long-run level of roughly $A^* = 1 - \delta/\beta_t$: trust raises it, barriers
  lower it. The household model simulates 1,000 households on an assumed village network.
- The constants in the formulas (for example the trust base 0.48) were **set by NDIM's developers as illustrative
  defaults, not estimated from data**. The sensitivity analysis shows that two of them, the adopter stop rate and the
  word-of-mouth rate, account for most of the variation in results (total indices about 0.88, against about 0.21 for
  the evidence inputs). **Calibrating them to real adoption data is the most important next step.**
- The uncertainty band shows only how far the evidence lets trust and barrier move; it leaves out doubt about the rules.

All formulas, derivations and values: *How it works* in the Studio, or `GET /engine/math`.

## Architecture

```
Browser ── Cloudflare Pages (cloudflare/public: Studio, manual, academy)
   │
   └── Cloudflare Worker (cloudflare/engine-container/src)
         ├── Container: FastAPI engine (backend/app, backend/Dockerfile)
         ├── D1: the engine's data folder mirrored (restored into each new container), usage counters, shared answers
         └── Workers AI: the research assistant's model (/__ai, capped per day and per visitor)

DeerFlow agents ── MCP server (mcp_server/) ── engine
Desktop app (desktop/, installer/) ── the same engine, local and offline, learning from your feedback
```

Learning from 👍/corrections happens only in the desktop app; the shared online demo never learns from visitors.

## Run it locally

```bash
docker build -f backend/Dockerfile -t ndim-engine .
docker run --rm -p 8010:8080 -e NDIM_DEPLOYMENT_MODE=local ndim-engine
# Studio: http://127.0.0.1:8010/
```

Or without Docker: `cd backend && pip install -r requirements.txt && python -m uvicorn app.main:app --port 8010`.

To use an AI model locally, open AI settings in the Studio (Ollama, LM Studio or an API key), or set
`NDIM_AGENT_PROVIDER` and the provider's key.

## Tests

Run in the engine image (no local Python setup needed):

```bash
docker run --rm -v $PWD:/src -w /src ndim-engine sh -c \
  'for t in test_encoder test_sensitivity test_model_soundness test_math_guide test_agent test_engine test_journey test_cors test_mirror test_network_model test_research; do python scripts/$t.py; done'
```

The suites cover the journey end to end (all eight sample datasets), model properties (shares stay valid, level rises
with trust and falls with barrier, outreach never lowers adoption), the guide's arithmetic against the engine, the
Sobol estimators against the Ishigami function, the encoder, the assistant's tools and access rules, and the mirror.

## Deploy

- **Engine (Cloudflare Worker + Container + D1 + Workers AI)**: see `cloudflare/engine-container/README.md`
  (`npx wrangler deploy` from that folder; secrets `NDIM_MIRROR_TOKEN`, `NDIM_AI_TOKEN`).
- **Pages (Studio, manual, academy)**: built from `cloudflare/public` on every push to `main`. After changing
  `backend/app/engine_assets`, run `python scripts/export_engine_static.py` and commit the result.
- **Desktop app and the earlier Cloud Run path**: `docs/DESKTOP_AND_CLOUD_RUN.md`.

## Releases

| Version | Date | Highlights |
|---|---|---|
| [v0.10.0-alpha.1](https://github.com/Naphymoro/nidm-rwanda-dashboard/releases/tag/v0.10.0-alpha.1) | 2026-10-07 | Cloudflare hosting, guided tour, How it works with derivations, teaching assistant with own-key option, population model fix, evidence-based bands, sensitivity analysis, encoder negation and topic lists |
| [v0.9.0-alpha.1](https://github.com/Naphymoro/nidm-rwanda-dashboard/releases/tag/v0.9.0-alpha.1) | 2026-05-15 | Desktop alpha: guided workflow, mode-specific encoding |
| [v0.8.0-alpha.1](https://github.com/Naphymoro/nidm-rwanda-dashboard/releases/tag/v0.8.0-alpha.1) | 2026-05-15 | First desktop packaging for Windows testers |

All releases: https://github.com/Naphymoro/nidm-rwanda-dashboard/releases · Notes: `RELEASE_NOTES.md`, `CHANGELOG.md`.

## Data and ethics

- Only records the researcher accepts reach a model; permission (research use, synthetic, unconfirmed) is recorded
  for every note, and the gate flags personal data and instruction-like text.
- Message drafts are for human review and editing. NDIM never posts, never targets named individuals, and never runs
  accounts. Counter-narratives must be truthful and cite evidence.
- The sample datasets are invented for teaching and marked synthetic; their Kinyarwanda notes should be checked by a
  speaker.

## Roadmap

1. Calibration: fit the stop and word-of-mouth rates to observed adoption series.
2. Social-media data import (exports first, official APIs where lawful) → echo-chamber and filter-bubble indicators,
   association rules over narratives, themes and places.
3. Prebunking studio grounded in inoculation and narrative theory, with the twin as a pre-screen.
4. Field-test loop (adaptive experiments) so real responses, not the model, decide which narratives work.
5. Monitoring agent on approved sources (alerts only).

## Repository layout

| Path | What |
|---|---|
| `backend/app` | the engine: journey, models, encoder, math guide, sensitivity, assistant, Studio assets |
| `cloudflare/engine-container` | the Worker, D1 migrations, Workers AI proxy |
| `cloudflare/public` | the static site (generated Studio export, manual, academy) |
| `mcp_server` | MCP server for DeerFlow and other agents |
| `scripts` | tests, static export, benchmarks, fine-tuning pipeline |
| `desktop`, `installer` | desktop app packaging |
| `docs` | guides and the earlier README |
