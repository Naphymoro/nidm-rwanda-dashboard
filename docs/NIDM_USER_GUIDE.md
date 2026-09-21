# NIDM user guide

NDIM has two user interfaces. The new Research Studio is the recommended place
to run a reviewable research experiment. The original workflow remains available
for the complete narrative-ingestion and evidence-governance sequence.

## Start the application

From the `nidm-rwanda-dashboard` directory:

```bash
export NDIM_DATA_DIR=/tmp/nidm-persistence-preview
.venv313/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8010
```

Keep the terminal open and visit `http://127.0.0.1:8010/`.

## Which interface should I use?

| Need | Route |
| --- | --- |
| New guided experiment with a saved plan, approval, checkpoints and resume | `/` |
| Explicit model, horizon and intervention controls | `/workbench` |
| Lessons and persisted learning checks | `/academy` |
| Original complete NIDM workflow | `/classic-workbench` |
| Original research-studio run history | `/classic-studio` |
| Original manual and stress-test instructions | `/manual` |
| Publication and methodology reference | `/publication` |

The new `/` route is not a replacement for every old screen. It is a smaller
research-execution surface. The original workflow is preserved at
`/classic-workbench` while the remaining advanced screens are migrated.

## Original NIDM workflow

Use `/classic-workbench` when you need the full sequence:

1. **Create or select a workspace**
   Choose a project such as NDIM Core or ClimateTales Rwanda. Workspace settings
   keep country, domain, provenance, repository and export context together.

2. **Collect and ingest narratives**
   Start with field notes, interview text, CSV observations, or PDF material.
   The ingestion layer normalizes the material into canonical narrative records,
   assigns IDs, preserves source metadata and calculates source hashes.

   Available backend endpoints are `POST /ingest/text`, `POST /ingest/csv` and
   `POST /ingest/pdf`. CSV/PDF upload requires the multipart dependency; text
   ingestion works offline without it.

3. **Review the evidence gate**
   Check source permission, consent, visibility, country/location, duplicates and
   provenance. Do not treat an unreviewed narrative as a model-ready observation.
   The SDMX-oriented upload gate and repository controls belong to the original
   workflow.

4. **Encode narratives**
   Choose manual, local/deterministic, AI, or hybrid encoding where configured.
   Encoding scores the narrative dimensions used by NDIM; it does not establish
   prevalence, causal effects or factual truth by itself.

5. **Diagnose inoculation needs**
   Review susceptibility, narrative resilience and counter-narrative suggestions.
   Keep the proposed response tied to the source evidence and mark uncertainty.

6. **Run models**
   Use compartmental simulation, agent-based/digital-twin views, or the hybrid
   workflow. Compare baseline and intervention settings and inspect assumptions,
   diagnostics and conservation/bounds checks.

7. **Review learning and policy implications**
   Use posterior/Bayesian and reinforcement-learning views as decision-support
   diagnostics. They are not a substitute for field validation or calibrated
   causal inference.

8. **Export and publish**
   Export the evidence ledger, SDMX/DSD packages, observations, audit material and
   policy brief. Use `/publication` for the scientific-method reference.

## New Research Studio workflow

Use `/` for a shorter, governed experiment:

1. Select a workspace and enter a research question.
2. Add source evidence and declare its provenance/consent.
3. Select an allowed skill such as evidence, scenario or sensitivity.
4. Review the generated plan, method, resource profile and warnings.
5. Approve the plan to start execution. Planning does not run tools automatically.
6. Monitor the durable run, download the audit JSON and review the completed brief.
7. Add a researcher review note. To change inputs, create a new experiment rather
   than editing a completed plan.

### Worked example: Energy Just Transition

Create a project named `Energy Just Transition`, then use this question:

```text
How can an energy transition expand reliable clean energy while protecting
households and workers affected by changes in traditional energy systems?
```

For a safe demonstration, paste the following synthetic interview set as the
source evidence and select **Synthetic teaching example** under Research context:

```text
SYNTHETIC INTERVIEW SET — ENERGY JUST TRANSITION — FOR DEMONSTRATION ONLY

Small enterprise owner: Reliable electricity would help me extend working hours,
but connection charges and unpredictable outages make planning difficult. I
support cleaner energy if the tariff remains affordable.

Rural household: Solar lighting has made evening study easier and reduced kerosene
use. My concern is the cost of replacing batteries and finding local repairs.

Traditional-fuel worker: A rapid shift could reduce my income. I would support it
if training and alternative work were available before the old work disappears.

Community representative: Residents want cleaner, reliable energy, but projects
should be discussed locally first. Fair access, transparent pricing and community
benefits matter.
```

Choose **Scenario comparison** to compare no intervention with a hypothetical
just-transition package. In this illustrative example, the intervention means a
combined programme of affordable connections, worker retraining, local
consultation, repair support and transparent tariffs. It is not a measured policy
effect. Review the plan before execution, then inspect the trust/barrier signals,
paired trajectories, numerical checks and limitations.

### Choose the explanation level

- **Guided — novice or policymaker:** explains what each field and output means;
  use results to structure questions and stakeholder discussion.
- **Researcher — methods and evidence:** emphasizes source provenance, parameter
  choices, comparison design and numerical checks.
- **Expert — full technical audit:** exposes tool outputs, execution events,
  environment details, checkpoints and code fingerprint for reproducibility.

The explanation level changes presentation only. It never changes the underlying
scientific method or silently upgrades a heuristic into evidence.

## Verification checklist

Run these checks after starting the server. They are designed to be observable by
a new user and auditable by a technical reviewer.

1. Open `/` and confirm the orientation panel, audience selector, project
   selector, **New project** button and function-coverage summary are visible.
2. Create `Energy Just Transition` with domain `energy just transition`. Confirm
   it becomes the active project and appears in the selector after refresh.
3. Click each audience level and confirm its guidance changes while the model
   controls do not silently change.
4. Click the scenario starter. Confirm the synthetic Energy Just Transition
   interview set fills the evidence field and the permission is `Synthetic teaching
   example`.
5. Clear the question or enter whitespace evidence. Confirm an actionable inline
   error appears and no plan is created.
6. Select Kinyarwanda or French and submit. Confirm execution is blocked with the
   explicit English-translation explanation.
7. Build a scenario plan. Confirm the status is `planned`, outputs are empty and
   the plan shows encoding, diagnosis, baseline, intervention, checks and brief.
8. Approve and execute. Confirm the status reaches `completed`, paired
   trajectories and heuristic signals appear, and the audit JSON/brief links work.
9. Add a review note, refresh, and reopen the run. Confirm the note and outputs
   persist.
10. Open `/function-coverage` and confirm all 13 classic stages are listed with
    inputs, actions, outputs, state/permission notes and migration status.

Observed automated checks for this revision:

- JavaScript syntax check: passed.
- Python compilation for the changed backend modules: passed.
- Rendered Studio/Workbench/Academy template smoke check: passed.
- Server-side invalid-text validation cases: passed.
- The existing research suite had previously passed 10/10. A rerun in the
  current managed sandbox stops at FastAPI `TestClient` startup with
  `Failed to create stream fd: Operation not permitted`; this is an environment
  limitation, not an observed application assertion failure. Complete the
  browser checklist above in a normal local terminal to verify the live server.

The new engine supports checkpointing, cancellation, restart recovery and resume.
It deliberately does not expose arbitrary code, shell commands, unbounded agents,
or an implicit LLM planner.

## Where data is stored

The configured data directory contains the local SQLite database, uploads,
exports, SDMX packages, logs, backups and workspaces. New engine runs are stored
under:

```text
workspaces/<workspace>/evidence/engine-runs/<run-id>.json
```

Use the desktop backup and restore functions for full backups. A full backup
contains sensitive research data; a support bundle contains diagnostics and logs
by default.

## What is migrated and what is not

The scientific source modules and original APIs remain available. The new shell
currently brings together reviewable planning, controlled scenario/sensitivity
execution, durable artifacts, workbench controls and Academy lessons. The old
multi-stage intake, SDMX gate, repository ledger, advanced digital-twin views,
publication workflow and some governance screens remain in the original UI until
they are migrated into the shared shell.

This separation is intentional: existing runs and evidence are preserved, and
the new interface does not silently convert or rewrite old records.
