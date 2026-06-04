# NDIM Engine Desktop Release Notes

## 0.9.0-alpha.9

This alpha rebuilds the tester package around the latest guided workflow, encoding, and demo-video changes.

- Adds a web-view demo route at `/demo-video` with a stage-by-stage player, PNG stage slides, and animated GIF fallback.
- Removes the confusing built-in sample loader from intake; evidence is now loaded manually, by file, or through the selected intake workflow.
- Makes encoding mode-specific: Manual, AI heuristic, and Hybrid show the relevant controls and results instead of exposing everything at once.
- Expands manual encoding to all six scientific variables: phi, trust, barrier, social influence, inoculation opportunity, and credibility/local grounding.
- Lets Manual, AI, and Hybrid encoding results be compared side-by-side and carried into the repository view.
- Replaces raw JSON-style status output with human-readable policy and audit text for non-technical testers.
- Adds clearer explanatory notes for how encoding feeds the compartmental model, agent model, digital twin, Bayesian update, and policy output.
- Refreshes tester artifacts and checksums so the portable ZIP and setup EXE match the current local app.

## 0.9.0-alpha.8

This alpha is a UI polish and workflow-correctness pass on the scientific workbench.

- Adds Focus group as a first-class intake evidence route with metadata, readiness checks, and manual documentation.
- Moves duplicate actions beside each existing workspace, so ClimateTales Rwanda is opened or copied from the existing workspace list rather than appearing as a create-new preset.
- Makes the Create workspace form blank and project-neutral, with explicit name and country requirements.
- Replaces text-only Close controls with compact close icons in modals and panels.
- Stretches the narrative repository preview across the workbench instead of squeezing it into the assistant column.
- Reframes the landing hero around NDIM Engine as the tool; workspace-specific domains such as clean cooking now appear as loaded project context after a workspace is active.
- Upgrades the landing description so NDIM is introduced as a scientific platform for narrative diffusion, misinformation, trust, social influence, digital-twin intervention testing, and policy-safe outputs.
- Gates the scientific task cards, repository preview, stage rail, and metrics until the user deliberately starts, opens, creates, or imports a workspace in the current session.
- Reworks Workspace Manager into a "Start from" list with From scratch first, followed by existing workspaces; NDIM Core is treated as a fallback/template instead of being shown as automatically active on landing.
- Keeps the button audit surface intact for Run current stage, focused task, activity log, workspace manager, repository view, full repository, manual links, import/export, and intake helpers.

## 0.9.0-alpha.7

This alpha previews a cleaner "from scratch" scientific workbench direction while preserving the existing NDIM workflow and backend behavior.

- Reframes the landing surface as a workspace operating console, with project loading, local/offline status, evidence routes, and workspace actions in one place.
- Moves the workflow into a focused active-task panel that explains the current scientific step, required input, scientific check, and status.
- Adds a compact Research Assistant caution card and repository preview beside the active task instead of crowding the hero with large static cards.
- Collapses the system dynamics map into an expandable drawer so the workflow diagram remains available without taking over the opening screen.
- Keeps core buttons and links wired: Run current stage, Open focused task, Activity log, Workspace manager, repository view, full repository, and manual links.

## 0.9.0-alpha.6

This alpha refines the opening workbench into a cleaner scientific workspace experience without changing the NDIM workflow logic.

- Rebalances the landing page into a large project workspace panel plus a compact side stack for project switching and research-assistant progress.
- Moves stage actions into a clearer current-stage card with Run current stage, Activity log, and Open focused task controls.
- Keeps the evidence-to-policy phase rail visible but less dominant, so users can understand the sequence without losing workspace context.
- Adds a cleaner evidence ledger summary with direct links to the manual, repository view, and full repository window.
- Keeps ClimateTales Rwanda as a workspace example while preserving the local-first evidence, modelling, digital-twin, inoculation, and policy-output workflow.

## 0.9.0-alpha.5

This alpha turns the opening experience into a simpler Start Workspace flow.

- Renames `#ClimateTales Rwanda` to `ClimateTales Rwanda` across workspace metadata and documentation.
- Adds a Start Workspace control with Continue last workspace, Open existing workspace, Create new workspace, Duplicate workspace, and Import workspace package actions.
- Reveals existing workspaces only when the user chooses to open an existing project, reducing landing-page clutter.
- Keeps the Research Assistant visible by default on desktop and gives it first-launch guidance before the workflow appears.
- Adds modern lightweight inline SVG icons for workspace actions, assistant guidance, evidence, governance, model, policy, and status cues.
- Uses progressive disclosure so the full NDIM stage list appears after a workspace session starts.
- Updates the manual and README around workspace loading, assistant guidance, and ClimateTales Rwanda as an example workspace.

## 0.9.0-alpha.4

This alpha turns the landing page into a workspace-first research cockpit.

- Adds a prominent workspace launchpad at the top of the workbench.
- Shows active workspace purpose, domain, evidence routes, evidence grade, and quick project actions.
- Adds quick workspace loading from the landing page without opening a separate modal first.
- Adds an agent-style Research Assistant cockpit with readiness score, worklist, next action, and run/log controls.
- Keeps the collapsible Research Assistant panel for deeper progress, scientific caution, and workspace guidance.
- Updates the manual to explain the workspace-first opening screen.

## 0.9.0-alpha.3

This alpha improves NDIM from a single fixed workflow into a workspace-based research engine.

- Adds local workspace storage with bundled `NDIM Core` and `ClimateTales Rwanda` presets.
- Adds backend endpoints to list, create, load, duplicate, import, export, and set active workspaces.
- Adds template-only, template-plus-stress-test, and full-backup workspace export modes.
- Adds a compact Workspace Manager in the top bar.
- Adds a collapsible Research Assistant / Workflow Guide panel with stage progress, next-best-action guidance, scientific interpretation, and policy caution.
- Makes governance sync include the active workspace identifier.
- Updates the manual with workspace and assistant guidance.

## Package

This Windows package is a local-first NDIM Engine desktop distribution. It installs and runs the research tool on the user's own machine.

## Files to publish

- `dist/NDIM Engine Setup.exe` - one-click Windows installer.
- `dist/NDIM-Engine-Windows-Portable.zip` - portable archive containing the bundled runtime. Users can unzip it and run `Launch NDIM Engine.cmd`.

## What is bundled

- NDIM Engine backend and integrated workflow UI.
- Bundled Python runtime and installed Python packages required by the current app.
- Manual and stress-test instructions.
- Full `stress_test_corpus/` CSV/TXT corpus.
- Local SQLite database support.

Users do not need to install Python, Node, npm, pip packages, or project requirements manually.

## Installation

1. Download `NDIM Engine Setup.exe`.
2. Double-click the installer.
3. Choose an install folder or keep the default.
4. Launch NDIM Engine from the Start Menu shortcut.
5. The app opens a local browser page at `http://127.0.0.1:8010` or the next available local port.

Portable option:

1. Download `NDIM-Engine-Windows-Portable.zip`.
2. Extract the ZIP.
3. Open `NDIM Engine Runtime/Launch NDIM Engine.cmd`.

## Data storage

The app stores local research data on the user's machine. In desktop mode the launcher creates folders for data, uploads, exports, logs, SDMX packages, backups, and support bundles.

## Stress-test corpus

The stress-test corpus is included in the package. It contains route-specific CSV files plus a bonus TXT narrative for testing narrative ingestion, SDMX readiness, approval, encoding, modelling, and policy-output workflow.

## Distribution

GitHub Releases is the recommended place to host the installer. Do not rely on local file paths as download links; upload `NDIM Engine Setup.exe` and `NDIM-Engine-Windows-Portable.zip` as release assets.

## Known limitations

- This Windows build is unsigned, so Windows SmartScreen may warn users on first launch.
- Advanced Torch/Pyro analytics are not bundled in this package; deterministic fallback analytics remain available.
- macOS and Linux packages must be built on those operating systems.
