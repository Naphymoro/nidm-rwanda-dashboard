# Changelog

## Unreleased

- Population model conserves people: two flows had one end only (the fading of views back to S added people;
  convinced people losing interest removed them), a leak of up to 0.2% of the population a day that a daily
  rescaling hid (about 39% cumulatively over 180 days). Every flow now has a source and a destination; the changes
  sum to zero, checked on the raw equations. Found by a tester.

## 0.10.0-alpha.1 (2026-10-07)

Web and engine release: NDIM is hosted on Cloudflare and teaches its own math.

- Hosting: Studio, manual and academy on Cloudflare Pages; the engine in a Cloudflare Container behind a Worker, its
  data mirrored in D1 so it survives restarts; clear "starting up" responses instead of errors; a read takes about
  0.6 s (was about 4 s).
- Guided tour with Back / Next over the real journey; eight synthetic datasets (clean cooking, vaccines, AI in the
  classroom, just transition; simple and thought-provoking) or your own notes by CSV.
- How it works: each step's model in symbols, derivation, the values NDIM uses (developer defaults, not estimates) and
  a worked example computed by the engine; every equation rendered with KaTeX.
- Research assistant on Workers AI (GLM 5.3 Flash) with daily and per-visitor caps, a teaching prompt, rendered math,
  and "use your own key" (OpenRouter, OpenAI, Anthropic, DeepSeek; the key stays in the browser).
- Security: hosted engines no longer learn from visitors' feedback (it reached every visitor's answers) and no longer
  list other visitors' questions.
- Model soundness: the population model's settled adopters now keep talking and can stop, so the long-run level depends
  on trust and barriers (every scenario used to drift towards full adoption); evidence-based uncertainty bands; Sobol
  sensitivity analysis (the stop and word-of-mouth rates drive most of the variation: calibration comes next).
- Encoder: negation ("I do not trust" is distrust), topic word lists, overlapping phrases counted once.
- Manual and curriculum corrected to the formulas the engine runs; the manual's equations render again.
- Network agent-based model, robustness across seven network shapes, messenger seeding comparison, Kinyarwanda notes
  with checked translations, AfriSenti sentiment classifier.
- Vercel removed: the repository no longer points to or records Vercel deployments.

## 0.8.0-alpha.1

- Added local-first NDIM Engine desktop packaging for Windows testers.
- Added bundled runtime package so testers do not need to install Python, Node, npm, pip, or requirements manually.
- Added stress-test corpus and stress-test guide to the packaged runtime.
- Added evidence governance, validation, repository lifecycle, SDMX export, and scientific-rigor UI updates.
- Added GitHub release workflow for versioned Windows release assets.
