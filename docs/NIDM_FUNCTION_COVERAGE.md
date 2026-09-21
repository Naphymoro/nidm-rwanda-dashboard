# NIDM function coverage and migration inventory

This is the acceptance inventory for the new Research Studio/Workbench. It is
deliberately explicit: “mapped” means the new shell provides the same user task,
not merely that a related Python function exists. “Classic only” means use
`/classic-workbench`.

## Route coverage

| Route | Purpose | Status |
| --- | --- | --- |
| `/` | Reviewable plan, evidence interpretation, scenario and sensitivity runs | Migrated |
| `/workbench` | Same engine with model and parameter controls open | Migrated |
| `/academy` | Guided lessons tied to real engine runs | Migrated |
| `/classic-workbench` | Full 13-stage NIDM workflow and evidence ledger | Classic only |
| `/classic-studio` | Earlier saved research explorations | Classic only |
| `/manual` | Original field manual and stress-test guidance | Classic/reference |
| `/publication` | Scientific and methods reference | Classic/reference |

## Classic stage inventory

| # | Classic workflow/screen | Main inputs and decisions | Actions | Outputs and states | New-shell status |
|---:|---|---|---|---|---|
| 1 | Narrative intake | Country, administrative levels, location, period, source type, evidence route, language, consent, visibility, interview text/file | Choose template, enter or upload evidence, split/stage narratives, edit metadata | Canonical narrative records, source hash, staged/pending records | Not migrated; use classic |
| 2 | SDMX gate | Required dimensions, code lists, data structure, source metadata, schema version | Validate payload, inspect errors, accept or return for correction | Valid/invalid gate result, validation messages, SDMX-ready records | Not migrated; use classic |
| 3 | Repository/evidence ledger | Review status, reviewer note, consent, visibility, duplicate flag, repository bucket, master repository settings | Approve, reject, flag, commit/uncommit, seal batch, sync ledger, export/import | Pending/approved/rejected/flagged/committed records, batch seal, sync result, audit event | Partially mapped by source evidence and provenance; full ledger classic only |
| 4 | Encoding | Manual dimensions E, C, τ, κ, B, S; AI/hybrid mode; model/provider choice; language | Score, save encoding, compare validation, rerun or review | Encoded narrative scores, themes, confidence, validation status | Partially migrated: deterministic English interpretation only |
| 5 | Compartmental model | S/M/T/I/R parameters, intervention, horizon, population/context assumptions | Run ODE-style simulation, inspect assumptions and trajectories | Time series, compartments, adoption, warnings and checks | Migrated as controlled scenario/sensitivity tool; classic parameter surface remains richer |
| 6 | Agent-based model | Household/agent characteristics, peer effects, network/proxy assumptions | Run agent simulation and compare with compartmental model | Agent/proxy trajectories and comparison | Not migrated to new shell; classic only |
| 7 | Digital twin | Narrative and field data streams, model outputs, feedback cadence | Run twin update/feedback loop | Updated state, feedback signals, model refresh status | Not migrated; classic only |
| 8 | Bayesian update | Priors, observations, trust/barrier likelihood inputs and uncertainty choices | Compute posterior | Posterior trust/barrier values and uncertainty summaries | Not migrated; classic only |
| 9 | RL optimizer | Reward, intervention/action space, episodes, learning controls and constraints | Run optimizer, inspect episodes, accept/reject recommended policy | Learned policy, episode history, recommended intervention | Not migrated; classic only |
| 10 | Regional analysis | Country/region/district lens, grouping and comparison selection | Filter, aggregate and compare places | Regional summaries and charts | Not migrated; classic only |
| 11 | Knowledge graph | Narratives, themes, places, people/groups and relationships | Build/explore graph | Nodes, edges, themes and place relationships | Not migrated; classic only |
| 12 | Inoculation lab | Narrative risk signals, misconception, target audience, counter-message constraints | Diagnose vulnerability, draft/test counter-narratives | Resilience diagnosis, counter-narrative candidates and warnings | Not migrated as a dedicated lab; new shell only includes bounded diagnosis step |
| 13 | Policy output | Reviewed evidence, model results, regional/graph/inoculation findings, policy audience and caveats | Run full policy pipeline, review, export | Policy brief, recommendation, audit/SDMX/export package and completion state | Partially migrated: draft brief/audit only; full policy pipeline classic only |

## Shared controls and state model

### Workspace/project

A workspace is a project container. It holds settings, evidence, templates,
exports and run history. Creating one does not create evidence or run a model.
The new shell supports create/select via **New project** and the project selector.

### New engine run states

`planned` means a plan exists but has not been approved. `queued` means approved
and waiting for the bounded worker. `running` means a tool is executing.
`cancelling` means a stop request is durable and will be honoured at a tool
boundary. `completed` means every planned tool checkpoint exists. `failed` means
the attempt stopped with saved checkpoints. `cancelled` means cancellation won.
`interrupted` means the server stopped and the run can be resumed if code and
environment fingerprints still match.

### Classic evidence states

Classic records can be staged, pending review, approved, rejected, flagged,
committed or uncommitted. A staged or encoded record is not automatically a
model-ready observation. Consent and reviewer decisions are separate from model
execution.

## Permissions and safety decisions

- `synthetic` identifies demonstration data and is safe for the worked example.
- `research_use` means the researcher has confirmed the declared use.
- `unconfirmed` preserves evidence for review but warns against sharing or policy use.
- English is currently executable by the bundled keyword encoder; other languages
  are blocked rather than silently translated.
- A reviewed prior run may be attached as context, but it cannot silently change
  model parameters.
- The new engine allows only named domain workflows; it does not execute shell
  commands, arbitrary code, remote tools or an unbounded agent.

## Edge cases and expected handling

| Case | Expected behavior |
| --- | --- |
| Empty/whitespace question or evidence | Inline error and HTTP 422; no plan is created |
| Evidence shorter than 20 characters | Inline error; ask for a meaningful excerpt |
| Unsupported language | Clear blocker explaining that an explicitly translated English source is required |
| Unconfirmed permission | Plan may be created with a warning; researcher must confirm before sharing |
| Agent-based intervention comparison | Blocked because the proxy does not use intervention strength |
| Zero intervention | Baseline and intervention deterministic trajectories must match |
| Duplicate start or active deletion | HTTP 409; the active run is protected |
| Stop during a tool call | Output is not published after cancellation wins; completed checkpoints remain |
| Server restart during active run | State becomes interrupted; resume is explicit |
| Code/environment fingerprint changed | Resume is blocked; create a new plan |
| Queue at capacity | HTTP 429 with retry guidance |
| Corrupt checkpoint | It is retained/logged and does not hide other runs |
| Invalid/unsafe backup archive | Restore stops before replacing data |

## Coverage conclusion

The new shell is a professional front end for a bounded subset of NIDM, not a
replacement for the classic workbench. The seven classic-only or partially
migrated areas above remain intentionally available at `/classic-workbench`.
Claims about policy should use reviewed evidence and the classic governance and
export stages until those functions are migrated.
