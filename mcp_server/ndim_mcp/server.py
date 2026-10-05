"""FastMCP server. Agents propose and read; only the engine's allowlisted tools produce scientific results.

Deliberately not exposed: deleting runs, saving researcher review notes, creating or editing workspaces, and
lesson answers. Those are researcher decisions or destructive, so they stay in the engine UI. Journey decisions that
belong to the researcher (evidence review, field observations, the export) need their quoted words.
"""
import asyncio
import time
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from . import audit, sweeps
from .client import EngineClient, EngineError, check_ids
from .config import Settings
from .journey import GUIDE, INTRO, LIMITS, journey_view
from .summaries import (DEFAULT_STRENGTH, ELIGIBLE, EXISTING_RUNS, NOTICE, REPORTING_RULES, TERMINAL, compare_runs,
                        existing_run_note, ineligible, summarize_plan, summarize_run, tutorial)

INSTRUCTIONS = """NDIM scientific engine: a deterministic digital twin of narrative diffusion and adoption.
Workflow: ndim_engine_status -> ndim_list_workspaces -> ndim_plan_experiment -> SHOW THE PLAN TO THE RESEARCHER AND GET
THEIR APPROVAL -> ndim_start_experiment -> ndim_wait_for_run / ndim_get_run -> ndim_get_brief.
Parameter sweeps: ndim_plan_sweep -> researcher approval -> ndim_run_sweep (runs and compares server-side).
Choose the workflow yourself (see ndim_plan_experiment's skill argument): a question about how an action, programme or
condition might change, affect, increase, reduce or improve adoption is a "scenario", not "evidence".
Results are illustrative and uncalibrated. Never present them as forecasts, estimated effects or validated findings, and
scope every claim to "this narrative" and "this model". Pass the researcher's question verbatim; never rephrase it.
A new question needs a new plan. Runs from ndim_list_runs are existing work: never present one as an answer; offer
its matching tutorial (an engine lesson) instead, and a new experiment on the researcher's own evidence.
Full journey: for a researcher who wants to go from their own field evidence through capture, encoding, models, the
digital twin, strategy and a policy export, use the 13-stage journey: ndim_journey_guide -> the researcher confirms their question, quoted back
verbatim -> ndim_journey_start -> ndim_journey_add_evidence -> ndim_journey_record_decisions (researcher decides) -> ndim_journey_run_stage for each stage
in order, explaining each result and asking before the next. ndim_journey_status shows where a journey stands.
Never approve a plan, accept evidence, supply field observations or write a review on the researcher's behalf."""

# Shown with the plan tool, where the agent decides the workflow. Keep in step with SKILL.md "Choose the workflow".
WORKFLOW_GUIDE = (
    'Workflow. Choose it yourself; do not leave it to "auto", which guesses from keywords and falls back to evidence. '
    '"scenario": the question asks how an action, programme or condition might change, affect, increase, reduce, '
    'improve or influence adoption, trust or uptake ("How might training more CHWs change adoption?", "Would a subsidy '
    'help?", "What if we ran a radio campaign?"). It runs the evidence steps too and adds a baseline vs intervention '
    'comparison. This is the default for any question about change. '
    '"sensitivity": "how much", "how strong", "at what level", "is more effort worth it". '
    '"evidence": only what the notes contain (signals, themes, risks, trust) with no change in view.')

READ = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)

Workspace = Annotated[str, Field(description='Workspace slug from ndim_list_workspaces, e.g. "ndim-core".')]
RunId = Annotated[str, Field(description='Run UUID returned by ndim_plan_experiment.')]
# A live agent turned "clean cooking adoption" into "adoption of gas stoves"; the question is the researcher's, not ours.
Question = Annotated[str, Field(min_length=8, max_length=1000, description=(
    "The researcher's question copied verbatim from their message. Do not rephrase, narrow, broaden or swap terms "
    '(e.g. do not turn "clean cooking" into "gas stoves" or "CHWs" into "health workers"), and do not add a prefix or '
    'context such as "in Rwanda" (the country has its own field). '
    'If it is too long or unclear, ask the researcher rather than rewriting it.'))]
Approval = Annotated[str, Field(min_length=12, max_length=1000, description=(
    "The researcher's own words approving THIS plan, quoted from the conversation. Only call this tool after the "
    'researcher has actually approved; never write this text yourself. It is stored in an audit log.'))]
# A live agent started a journey for "... adoption in Rwanda?" when the researcher had not said "in Rwanda".
QuestionConfirmation = Annotated[str, Field(min_length=2, max_length=1000, description=(
    "The researcher's reply after you showed them the question in quotes, exactly as you will pass it, and asked them to "
    'confirm or correct it, e.g. "Yes, that is my question." Only call after they replied; never write this text '
    'yourself. If they corrected it, pass their corrected wording as question. It is stored in an audit log.'))]
JourneyId = Annotated[str, Field(description='Journey UUID returned by ndim_journey_start.')]
Stage = Literal['encoding', 'compartmental', 'agents', 'digital', 'bayes', 'rl', 'regional', 'graph', 'inoculation', 'policy']


class EvidenceRecord(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=20000, description='The story or field note, unchanged, in its '
        'original language. Never replace it with a translation.')]
    admin_unit: Annotated[str, Field(min_length=1, max_length=240, description='Place, as the researcher gave it, e.g. "Kicukiro / Niboye".')]
    source_name: Annotated[str, Field(min_length=1, max_length=240, description='Who or what the record came from, e.g. "Field team interview 4".')]
    period: Annotated[str, Field(min_length=1, max_length=60, description='When it was collected, e.g. "2026-Q2". Ask; do not guess.')]
    source_type: Literal['field_note', 'interview', 'focus_group', 'survey_open_text', 'citizen_report', 'document'] = 'field_note'
    language: Literal['en', 'rw', 'fr', 'other'] = 'en'
    consent: Annotated[Literal['synthetic', 'research_use', 'unconfirmed'], Field(description=(
        '"research_use" only if the researcher confirmed permission; "synthetic" for demo data; otherwise "unconfirmed".'))] = 'unconfirmed'
    translation_en: Annotated[str | None, Field(min_length=1, max_length=20000, description=(
        'For a record not in English: the English translation the researcher gave you, word for word. Never your own '
        'translation. Keyword scores read it (sentiment reads the original); without it a non-English record is blocked.'))] = None
    translation_checked_by: Annotated[str | None, Field(min_length=1, max_length=240, description=(
        'Name of the person who checked that translation, as the researcher said it. Ask; never fill it in yourself.'))] = None


class EvidenceDecision(BaseModel):
    record_id: str
    decision: Literal['accept', 'reject']
    reason: Annotated[str | None, Field(max_length=400, description="The researcher's reason, if they gave one.")] = None


def create_server(settings=None, client=None, host='127.0.0.1', port=8000):
    settings = settings or Settings.from_env()
    engine = client or EngineClient(settings)
    mcp = FastMCP('ndim-engine', instructions=INSTRUCTIONS, host=host, port=port)

    async def fetch_run(workspace_id, run_id):
        check_ids(workspace_id, run_id)
        return await engine.request('GET', f'/engine/workspaces/{workspace_id}/runs/{run_id}')

    lesson_cache = {}

    async def tutorial_for(skill, workspace_id):
        """The engine lesson for a workflow; None if the engine has none (tutorials are an offer, never a blocker)."""
        if not lesson_cache:
            try:
                lesson_cache.update({lesson['skill']: lesson for lesson in (await engine.request('GET', '/engine/lessons'))['lessons']})
            except Exception:  # noqa: BLE001 - an unreachable or odd lessons endpoint must not break the caller
                return None
        lesson = lesson_cache.get(skill)
        return tutorial(lesson, workspace_id, settings.public_url or settings.engine_url) if lesson else None

    async def lost_journey(workspace_id, journey_id, error):
        """A live agent dropped a segment of the UUID, then started a second journey and re-entered the evidence.
        Name the journey it most likely meant and say the original is intact."""
        check_ids(workspace_id)
        given = journey_id.strip().lower()
        try:
            rows = (await engine.request('GET', f'/engine/workspaces/{workspace_id}/journeys'))['journeys']
        except Exception:  # noqa: BLE001 - the hint is a courtesy; the original error still stands
            rows = []
        matches = [row for row in rows if given[:8] == row['journey_id'][:8] or given[-12:] == row['journey_id'][-12:]]
        keep = ' The journey and every stage already run are unchanged. Do not start a new journey to recover from this.'
        if len(matches) == 1:
            row = matches[0]
            return EngineError(f'{error} Did you mean {row["journey_id"]!r} (question: "{row["question"]}", '
                               f'{row["stages_done"]} stage(s) done)? Copy that id exactly, character for character.' + keep)
        return EngineError(f'{error} Take the journey_id exactly from the last journey tool result, or call '
                           'ndim_journey_list.' + keep)

    async def journey_call(method, workspace_id, journey_id, suffix='', audit_fields=None, **kwargs):
        try:
            check_ids(workspace_id, journey_id=journey_id)
            body = await engine.request(method, f'/engine/workspaces/{workspace_id}/journeys/{journey_id}{suffix}', **kwargs)
        except EngineError as exc:
            if str(exc).startswith('Invalid journey_id') or exc.status == 404:
                raise await lost_journey(workspace_id, journey_id, str(exc)) from exc
            raise
        if audit_fields:  # after the engine accepted it: a refused stage or review must leave no approval behind
            audit.record(settings, workspace_id=workspace_id, journey_id=journey_id, **audit_fields)
        return journey_view(body)

    async def wait(workspace_id, run_id, seconds):
        seconds = max(0, min(seconds, settings.max_wait_seconds))
        deadline = time.monotonic() + seconds
        run = await fetch_run(workspace_id, run_id)
        while run['status'] not in TERMINAL | {'planned'} and time.monotonic() < deadline:
            await asyncio.sleep(0.5)
            run = await fetch_run(workspace_id, run_id)
        return run

    @mcp.tool(annotations=READ)
    async def ndim_engine_status() -> dict:
        """Check the NDIM engine is reachable and see its resource limits and capabilities.

        Call first. Reports worker_limit (how many experiments can run at once; the engine queue holds 8) and
        what the engine cannot do ("unavailable")."""
        health, caps = await asyncio.gather(engine.request('GET', '/health'), engine.request('GET', '/engine/capabilities'))
        resources = caps['resources']
        return {'reachable': True, 'engine_url': settings.engine_url, 'status': health.get('status'),
                'deployment_mode': health.get('deployment_mode'), 'offline_ready': health.get('offline_ready'),
                'warnings': health.get('warnings', []),
                'resources': {key: resources[key] for key in ('cpu_available', 'memory_available_mb', 'recommended_profile',
                                                              'worker_limit', 'profiles', 'dependencies')},
                'planner': caps['planner'], 'implemented': caps['implemented'], 'unavailable': caps['unavailable'],
                'access': caps['access']}

    @mcp.tool(annotations=READ)
    async def ndim_list_workspaces() -> dict:
        """List research workspaces (id, name, domain, countries). Runs belong to exactly one workspace."""
        data = await engine.request('GET', '/workspaces')
        rows = data['workspaces'] if isinstance(data, dict) and 'workspaces' in data else data
        return {'workspaces': [{key: row.get(key) for key in ('workspace_id', 'name', 'description', 'domain', 'countries', 'updated_at')}
                               for row in rows]}

    @mcp.tool(annotations=READ)
    async def ndim_list_lessons() -> dict:
        """Return the engine's teaching lessons (tutorials) and its synthetic sample field notes.

        Each lesson teaches one workflow (evidence, scenario, sensitivity). To run one here, plan it with its lesson_id,
        its question and the synthetic sample (consent="synthetic"); the researcher answers its check in the web app.
        The sample is synthetic, not real data."""
        data = await engine.request('GET', '/engine/lessons')
        public = settings.public_url or settings.engine_url
        for lesson in data.get('lessons', []):
            lesson['link'] = tutorial(lesson, 'ndim-core', public)['link']
        return data

    @mcp.tool(annotations=WRITE)
    async def ndim_plan_experiment(
        workspace_id: Workspace,
        question: Question,
        evidence: Annotated[str, Field(min_length=20, max_length=20000, description='Source narrative or field notes, in '
            'English. Non-English text is blocked by the engine. If you translate, tell the researcher and get their '
            'confirmation first.')],
        skill: Annotated[Literal['scenario', 'sensitivity', 'evidence', 'auto'], Field(description=WORKFLOW_GUIDE)],
        consent: Annotated[Literal['synthetic', 'research_use', 'unconfirmed'], Field(description=(
            '"research_use" only if the researcher confirmed permission to use this evidence; "synthetic" for demo data; '
            'otherwise "unconfirmed". Never upgrade this yourself.'))] = 'unconfirmed',
        model: Annotated[Literal['compartmental', 'agent_based', 'hybrid'], Field(description='Model family. agent_based ignores '
            'intervention strength, so it is blocked for scenario and sensitivity workflows.')] = 'compartmental',
        profile: Annotated[Literal['auto', 'economy', 'balanced', 'thorough'], Field(description='Sensitivity grid density: 3, 7 or 11 points.')] = 'auto',
        horizon_days: Annotated[int, Field(ge=7, le=365)] = 90,
        intervention_strength: Annotated[float, Field(ge=0, le=1, description='The only intervention lever in the model. '
            'The researcher\'s intervention (e.g. "more trained CHWs") maps onto this abstract 0-1 value; the engine does '
            'not model CHW counts, prices or channels. 0.3 = moderate.')] = DEFAULT_STRENGTH,
        initial_adoption: Annotated[float, Field(ge=0, le=1)] = 0.1,
        narrative_influence: Annotated[float, Field(ge=0, le=1)] = 0.38,
        language: Annotated[Literal['en', 'rw', 'fr', 'other'], Field(description='Language of the evidence text.')] = 'en',
        expertise: Annotated[Literal['guided', 'researcher', 'expert'], Field(description='Explanation level stored with the run.')] = 'guided',
        source_name: Annotated[str, Field(min_length=1, max_length=240)] = 'Researcher-supplied field note',
        prior_run_ids: Annotated[list[str] | None, Field(max_length=3, description='Completed runs that carry a researcher review, '
            'used as context only; they never change model parameters.')] = None,
        strength_reason: Annotated[str | None, Field(min_length=8, max_length=400, description=(
            'Optional: why this intervention_strength. Quote the researcher only if they actually gave a value or level; '
            'never attribute the default to them. Shown to the researcher before approval and kept in the audit log.'))] = None,
        lesson_id: Annotated[Literal['evidence', 'scenario', 'sensitivity'] | None, Field(description=(
            'Only when running a tutorial from ndim_list_lessons: its id. skill must match the lesson, and the run then '
            'counts as that lesson in the web app, where the researcher answers its check.'))] = None,
    ) -> dict:
        """Create a reviewable experiment plan. Nothing executes until ndim_start_experiment.

        Set skill explicitly: a question about how something might change adoption is a scenario, not evidence.
        Returns the steps, warnings and any blockers. Present them to the researcher before asking for approval,
        and for a scenario say plainly that their intervention is represented only by intervention_strength."""
        check_ids(workspace_id)
        prior_run_ids = prior_run_ids or []
        for prior in prior_run_ids:
            check_ids(workspace_id, prior)
        payload = {'workspace_id': workspace_id, 'question': question, 'evidence': evidence, 'consent': consent,
                   'skill': skill, 'model': model, 'profile': profile, 'horizon_days': horizon_days,
                   'intervention_strength': intervention_strength, 'initial_adoption': initial_adoption,
                   'narrative_influence': narrative_influence, 'language': language, 'expertise': expertise,
                   'source_name': source_name, 'prior_run_ids': prior_run_ids}
        if lesson_id:
            payload['lesson_id'] = lesson_id
        plan = summarize_plan(await engine.request('POST', '/engine/plans', json=payload), strength_reason)
        if plan['intervention_mapping']:  # the engine forbids extra fields, so the stated reason lives in the audit log
            audit.record(settings, 'ndim_plan_experiment', workspace_id=workspace_id, run_id=plan['run_id'],
                         intervention_strength=intervention_strength, strength_reason=strength_reason)
        return plan

    async def gated(tool, action, workspace_id, run_id, approval_statement, wait_seconds):
        check_ids(workspace_id, run_id)
        # Check first: an approval must never be logged for a run the engine will refuse (a live agent "started" an
        # old completed run it had found with ndim_list_runs). The engine still enforces this if the status changes.
        run = await fetch_run(workspace_id, run_id)
        if run['status'] not in ELIGIBLE[action]:
            raise EngineError(ineligible(run, action, await tutorial_for(run['skill'], workspace_id)))
        audit.record(settings, tool, workspace_id=workspace_id, run_id=run_id, approval_statement=approval_statement)
        await engine.request('POST', f'/engine/workspaces/{workspace_id}/runs/{run_id}/{action}', retry_busy=True)
        return summarize_run(await wait(workspace_id, run_id, wait_seconds))

    @mcp.tool(annotations=WRITE)
    async def ndim_start_experiment(workspace_id: Workspace, run_id: RunId, approval_statement: Approval,
                                    wait_seconds: Annotated[int, Field(ge=0, le=120, description='Seconds to wait for '
                                        'completion before returning progress.')] = 30) -> dict:
        """Run an approved plan. Requires the researcher's explicit approval of this exact plan.

        Retries automatically while the engine queue is full. If it has not finished within wait_seconds,
        call ndim_wait_for_run."""
        return await gated('ndim_start_experiment', 'start', workspace_id, run_id, approval_statement, wait_seconds)

    @mcp.tool(annotations=WRITE)
    async def ndim_resume_experiment(workspace_id: Workspace, run_id: RunId, approval_statement: Approval,
                                     wait_seconds: Annotated[int, Field(ge=0, le=120)] = 30) -> dict:
        """Resume a failed, interrupted or cancelled run from its saved checkpoints. Also needs researcher approval.

        Fails with 409 if the scientific code or environment changed since planning; then create a new plan."""
        return await gated('ndim_resume_experiment', 'resume', workspace_id, run_id, approval_statement, wait_seconds)

    @mcp.tool(annotations=WRITE)
    async def ndim_cancel_experiment(workspace_id: Workspace, run_id: RunId) -> dict:
        """Request cancellation. In-flight tools finish first; completed checkpoints are kept."""
        check_ids(workspace_id, run_id)
        audit.record(settings, 'ndim_cancel_experiment', workspace_id=workspace_id, run_id=run_id)
        await engine.request('POST', f'/engine/workspaces/{workspace_id}/runs/{run_id}/cancel')
        return summarize_run(await fetch_run(workspace_id, run_id))

    @mcp.tool(annotations=READ)
    async def ndim_wait_for_run(workspace_id: Workspace, run_id: RunId,
                                timeout_seconds: Annotated[int, Field(ge=0, le=120)] = 60) -> dict:
        """Wait until the run finishes or the timeout passes, then return its summary."""
        return summarize_run(await wait(workspace_id, run_id, timeout_seconds))

    @mcp.tool(annotations=READ)
    async def ndim_get_run(workspace_id: Workspace, run_id: RunId,
                           include_trajectories: Annotated[bool, Field(description='Include every daily trajectory point. '
                               'Large (about 90 rows per simulation step); leave false unless you must plot or re-analyse.')] = False) -> dict:
        """Get a run's status, encoded signals, per-simulation statistics, comparison and numerical checks."""
        return summarize_run(await fetch_run(workspace_id, run_id), include_trajectories)

    @mcp.tool(annotations=READ)
    async def ndim_list_runs(workspace_id: Workspace, offset: Annotated[int, Field(ge=0)] = 0,
                             limit: Annotated[int, Field(ge=1, le=100)] = 30) -> dict:
        """List what has already been run in a workspace, newest first, each with its matching tutorial.

        Not a way to answer a question: plan a new experiment. Run ids are withheld on purpose."""
        check_ids(workspace_id)
        listing = await engine.request('GET', f'/engine/workspaces/{workspace_id}/runs', params={'offset': offset, 'limit': limit})
        # Told not to, live agents still fetched an old run found here and presented its results. Without the id they
        # cannot; a researcher who wants a specific run can paste its id from the web app.
        rows = [{key: row.get(key) for key in ('title', 'skill', 'status', 'created_at', 'reviewed', 'lesson_id')}
                | {'matching_tutorial': await tutorial_for(row.get('skill'), workspace_id)} for row in listing.get('runs', [])]
        return {'runs': rows, 'total': listing.get('total'), 'next': EXISTING_RUNS}

    @mcp.tool(annotations=READ)
    async def ndim_get_brief(workspace_id: Workspace, run_id: RunId) -> dict:
        """Return the engine-generated research brief (Markdown) for a completed run planned in this conversation.

        For an earlier run the researcher did not plan here, offer the matching tutorial instead of this brief."""
        check_ids(workspace_id, run_id)
        markdown = await engine.request('GET', f'/engine/workspaces/{workspace_id}/runs/{run_id}/artifacts/brief', text=True)
        run = await fetch_run(workspace_id, run_id)
        # The brief can stand in for a report, so it carries the same instructions, plus where the run came from.
        return {'run_id': run_id, 'question': run['title'], 'created_at': run.get('created_at'), 'markdown': markdown,
                'notice': NOTICE, 'reporting_rules': REPORTING_RULES,
                'matching_tutorial': (found := await tutorial_for(run['skill'], workspace_id)),
                'next': existing_run_note(run, found) + ' If it was planned and approved in this conversation, report '
                        'it as follows. ' + summarize_run(run).get('next', REPORTING_RULES)}

    async def compare(workspace_id, run_ids, reference_id=None):
        check_ids(workspace_id)
        for run_id in run_ids:
            check_ids(workspace_id, run_id)
        gate = asyncio.Semaphore(4)

        async def one(run_id):
            async with gate:
                return await fetch_run(workspace_id, run_id)
        return compare_runs(await asyncio.gather(*(one(run_id) for run_id in dict.fromkeys(run_ids))), reference_id)

    @mcp.tool(annotations=READ)
    async def ndim_compare_runs(workspace_id: Workspace,
                                run_ids: Annotated[list[str], Field(min_length=2, max_length=24)],
                                reference_run_id: Annotated[str | None, Field(description='For a one-at-a-time sweep: the '
                                    'base run. Each other run may then differ from it in exactly one factor.')] = None) -> dict:
        """Tabulate completed runs side by side and audit their comparability.

        Aggregation happens here, deterministically, so you do not need to copy numbers between calls. Read
        comparability.notes: the comparison is only controlled when a single factor varies on identical evidence."""
        if reference_run_id is not None:
            check_ids(workspace_id, reference_run_id)
        return await compare(workspace_id, run_ids, reference_run_id)

    @mcp.tool(annotations=WRITE)
    async def ndim_plan_sweep(
        workspace_id: Workspace,
        question: Question,
        evidence: Annotated[str, Field(min_length=20, max_length=20000, description='Sent unchanged with every plan, so all '
            'runs share one source hash. Do not paste it repeatedly yourself; call this tool once.')],
        vary: Annotated[dict[str, list[float]], Field(description=(
            'Factors to vary and their values, e.g. {"narrative_influence": [0.2, 0.4, 0.6]}. Allowed factors: '
            'narrative_influence, initial_adoption, intervention_strength (0-1) and horizon_days (7-365). At most 12 '
            'values per factor.'))],
        consent: Annotated[Literal['synthetic', 'research_use', 'unconfirmed'], Field(description='As in ndim_plan_experiment.')] = 'unconfirmed',
        mode: Annotated[Literal['one_at_a_time', 'grid'], Field(description=(
            'one_at_a_time: a base run plus each value of each factor alone (attributable). grid: every combination '
            '(interactions, but differences cannot be attributed to one factor). At most 24 runs.'))] = 'one_at_a_time',
        model: Annotated[Literal['compartmental', 'hybrid'], Field(description='agent_based cannot express an intervention.')] = 'compartmental',
        horizon_days: Annotated[int, Field(ge=7, le=365)] = 90,
        intervention_strength: Annotated[float, Field(ge=0, le=1)] = 0.3,
        initial_adoption: Annotated[float, Field(ge=0, le=1)] = 0.1,
        narrative_influence: Annotated[float, Field(ge=0, le=1)] = 0.38,
        language: Annotated[Literal['en', 'rw', 'fr', 'other'], Field(description='Language of the evidence text.')] = 'en',
        source_name: Annotated[str, Field(min_length=1, max_length=240)] = 'Researcher-supplied field note',
    ) -> dict:
        """Create a set of scenario plans that differ only in the parameters you list. Nothing executes yet.

        Every run uses the scenario workflow (baseline vs intervention) on identical evidence. The engine is
        deterministic, so a sweep varies parameters; repeating an identical run adds nothing."""
        check_ids(workspace_id)
        base = {'narrative_influence': narrative_influence, 'initial_adoption': initial_adoption,
                'intervention_strength': intervention_strength, 'horizon_days': horizon_days}
        try:
            items = sweeps.design(base, vary, mode)
        except ValueError as exc:
            raise EngineError(str(exc)) from exc
        planned = []
        for item in items:
            payload = {'workspace_id': workspace_id, 'question': question, 'evidence': evidence, 'consent': consent,
                       'skill': 'scenario', 'model': model, 'language': language, 'source_name': source_name,
                       **item['values']}
            plan = summarize_plan(await engine.request('POST', '/engine/plans', json=payload))
            planned.append({'run_id': plan['run_id'], 'label': item['label'], 'varied': item['varied'],
                            'blockers': plan['blockers']})
            if plan['blockers']:  # blockers do not depend on the varied factors, so stop at the first
                return {'planned': planned, 'blocked': True, 'warnings': plan['warnings'],
                        'next': 'BLOCKED: ' + plan['blockers'][0] + ' Explain this to the researcher and start a new sweep.'}
        return {'mode': mode, 'base': base, 'varied_factors': list(vary), 'planned': planned, 'n_runs': len(planned),
                'reference_run_id': planned[0]['run_id'] if mode == 'one_at_a_time' else None,
                'shared': {'source_sha256': plan['provenance']['source_sha256'], 'code_version': plan['provenance']['code_version'],
                           'model': model, 'consent': consent},
                'warnings': plan['warnings'],
                'question': question,
                'next': 'Show this design to the researcher, quoting the question exactly so they can confirm it is '
                        'theirs, and obtain explicit approval before calling ndim_run_sweep '
                        'with these run_ids. Do not approve on their behalf.'}

    @mcp.tool(annotations=WRITE)
    async def ndim_run_sweep(
        workspace_id: Workspace,
        run_ids: Annotated[list[str], Field(min_length=2, max_length=sweeps.MAX_SWEEP_RUNS, description='All run_ids from ndim_plan_sweep.')],
        approval_statement: Approval,
        reference_run_id: Annotated[str | None, Field(description='reference_run_id from ndim_plan_sweep (one_at_a_time only).')] = None,
        wait_seconds: Annotated[int, Field(ge=0, le=120)] = 60,
    ) -> dict:
        """Run an approved sweep with the engine's queue limits respected, then compare the results.

        Needs the researcher's approval of the whole design. One failed run does not discard the others; check
        errors and comparison.excluded."""
        check_ids(workspace_id)
        for run_id in run_ids:
            check_ids(workspace_id, run_id)
        if reference_run_id is not None:
            check_ids(workspace_id, reference_run_id)
        unique = list(dict.fromkeys(run_ids))
        gate = asyncio.Semaphore(4)
        errors = []

        async def begin(run_id):
            async with gate:
                try:
                    run = await fetch_run(workspace_id, run_id)
                    if run['status'] not in ELIGIBLE['start']:  # as in gated(): no approval logged for a refused run
                        raise EngineError(ineligible(run, 'start', await tutorial_for(run['skill'], workspace_id)))
                    audit.record(settings, 'ndim_run_sweep', workspace_id=workspace_id, run_id=run_id,
                                 approval_statement=approval_statement)
                    await engine.request('POST', f'/engine/workspaces/{workspace_id}/runs/{run_id}/start', retry_busy=True)
                    return run_id
                except EngineError as exc:
                    errors.append({'run_id': run_id, 'error': str(exc)})

        started = [run_id for run_id in await asyncio.gather(*(begin(run_id) for run_id in unique)) if run_id]
        finished = await asyncio.gather(*(wait(workspace_id, run_id, wait_seconds) for run_id in started))
        return {'comparison': compare_runs(list(finished), reference_id=reference_run_id), 'errors': errors,
                'still_running': [run['run_id'] for run in finished if run['status'] not in TERMINAL],
                'next': 'Report with the comparability notes; a grid shows sensitivity, not uncertainty. If runs are '
                        'still running, call ndim_wait_for_run then ndim_compare_runs. ' + REPORTING_RULES}

    # --- The 13-stage journey: capture -> analysis -> digital twin -> strategy -> export -----------------------------

    @mcp.tool(annotations=READ)
    async def ndim_journey_guide() -> dict:
        """Explain the 13-stage NDIM journey: what each stage does, what it needs, and which need the researcher.

        Use it to describe the journey before starting, or when the researcher asks what a stage is."""
        guide = await engine.request('GET', '/engine/journey/stages')
        public = settings.public_url or settings.engine_url
        return {'stages': [{key: stage[key] for key in ('number', 'id', 'phase', 'title', 'does', 'needs', 'researcher_decision')}
                           | {'optional': stage.get('optional', False), 'limits': LIMITS[stage['id']]} for stage in guide['stages']],
                'principles': guide['principles'],
                'web_app': f'{public}/classic-workbench',
                'intro': INTRO,
                'next': ('Show the researcher the intro field word for word, as markdown. Then show their question back in '
                         'quotes, exactly as you will pass it to ndim_journey_start (ask for it if they have not given '
                         'one), and ask them to confirm or correct it. Call ndim_journey_start only after they reply, with '
                         'that reply as question_confirmation. ' + GUIDE)}

    @mcp.tool(annotations=READ)
    async def ndim_journey_list(workspace_id: Workspace) -> dict:
        """List a workspace's journeys, newest first. Resume one only if the researcher says it is theirs."""
        check_ids(workspace_id)
        data = await engine.request('GET', f'/engine/workspaces/{workspace_id}/journeys')
        return {**data, 'next': 'These may belong to other researchers or conversations. Continue one only when the '
                                'researcher confirms it is theirs; otherwise start a new journey.'}

    @mcp.tool(annotations=WRITE)
    async def ndim_journey_start(workspace_id: Workspace, question: Question, question_confirmation: QuestionConfirmation,
                                 country: Annotated[str, Field(min_length=2, max_length=80)] = 'Rwanda') -> dict:
        """Start a 13-stage journey for the researcher's question. Nothing is scored or modelled yet.

        Call ndim_journey_guide first. Before this call, show the researcher the question in quotes exactly as you will
        pass it and wait for them to confirm or correct it."""
        check_ids(workspace_id)
        body = await engine.request('POST', f'/engine/workspaces/{workspace_id}/journeys',
                                    json={'question': question, 'country': country})
        audit.record(settings, 'ndim_journey_start', workspace_id=workspace_id, journey_id=body['journey_id'],
                     question=question, question_confirmation=question_confirmation)
        view = journey_view(body)
        # A live agent skipped ndim_journey_guide and asked for evidence without saying where the journey goes. Given only
        # the phase names, it described the twin as "to validate findings" and the export as "actionable policy outputs".
        # Told to quote the question and add nothing, live agents still wrote "how trusted messengers can change ...
        # adoption in Rwanda": a paraphrase with the country folded in. A finished sentence names the country apart.
        view['opening'] = (f'The journey has started with your question, exactly as you confirmed it: "{view["question"]}" '
                           f'The setting is {view["country"]}.')
        view['next'] = (f'Use journey_id {view["journey_id"]} exactly for every later call in this journey; start only one '
                        'journey per question. Begin your reply with the opening sentence word for word; after it, refer '
                        'to the question only by quoting it exactly, never by paraphrase. Before asking for evidence, '
                        'tell the researcher what lies ahead, using the text below word for word, unless you already '
                        'showed it from ndim_journey_guide; do not list the stages any other way.\n\n' + INTRO + '\n\n'
                        + view['next'])
        return view

    @mcp.tool(annotations=READ)
    async def ndim_journey_status(workspace_id: Workspace, journey_id: JourneyId) -> dict:
        """Where a journey stands: each stage's status, the records and their gate results, and the next stage."""
        return await journey_call('GET', workspace_id, journey_id)

    @mcp.tool(annotations=WRITE)
    async def ndim_journey_add_evidence(workspace_id: Workspace, journey_id: JourneyId,
                                        records: Annotated[list[EvidenceRecord], Field(min_length=1, max_length=50)]) -> dict:
        """Stages 1-2: add the researcher's records and run the SDMX gate on each (metadata, English, personal data,
        instruction-like text, duplicates). Records are stored unchanged; one record per story or note."""
        return await journey_call('POST', workspace_id, journey_id, '/evidence',
                                  json={'records': [record.model_dump(exclude_none=True) for record in records]})

    @mcp.tool(annotations=WRITE)
    async def ndim_journey_record_decisions(workspace_id: Workspace, journey_id: JourneyId,
                                           decisions: Annotated[list[EvidenceDecision], Field(min_length=1, max_length=50)],
                                           approval_statement: Annotated[str, Field(min_length=2, max_length=1000, description=(
                                               "The researcher's message giving these accept/reject decisions. Never decide "
                                               'for them. Copy it character for character from the researcher\'s message, however short ("Yes, continue." is fine). '
            'Never compose or expand it: a live agent recorded "Please proceed with drafting the policy output." when the '
            'researcher had written only "Yes, continue."'))]) -> dict:
        """Stage 3: record the researcher's accept or reject decision for each record. Only accepted records reach a model."""
        return await journey_call('POST', workspace_id, journey_id, '/review',
                                  audit_fields={'tool': 'ndim_journey_record_decisions', 'approval_statement': approval_statement,
                                                'decisions': [d.model_dump() for d in decisions]},
                                  json={'decisions': [d.model_dump() for d in decisions], 'approval_statement': approval_statement})

    @mcp.tool(annotations=WRITE)
    async def ndim_journey_run_stage(
        workspace_id: Workspace, journey_id: JourneyId, stage: Stage,
        approval_statement: Annotated[str | None, Field(min_length=2, max_length=1000, description=(
            "Required for digital and policy: the researcher's message giving their field observations (digital) or "
            'answering yes to the export question (policy). Copy it character for character from the researcher\'s message, however short ("Yes, continue." is fine). '
            'Never compose or expand it: a live agent recorded "Please proceed with drafting the policy output." when the '
            'researcher had written only "Yes, continue."'))] = None,
        observed_adoption: Annotated[float | None, Field(ge=0, le=1, description='digital: adoption share the researcher '
            'observed in the field (0-1). Ask for it; there is no default.')] = None,
        trust_shift: Annotated[float | None, Field(ge=-1, le=1, description='digital: change in trust the researcher observed '
            'since the evidence was collected, -1 to 1; 0 if they saw none. Ask.')] = None,
        barrier_shift: Annotated[float | None, Field(ge=-1, le=1, description='digital: change in adoption barriers observed, '
            '-1 to 1; 0 if none. Ask.')] = None,
        observed_series: Annotated[list[float] | None, Field(min_length=3, max_length=365, description='digital, optional: '
            'observed adoption shares over time (at least 3), from the researcher\'s data. Lets the Bayesian stage fit the '
            'adoption curve; never fill it from model output.')] = None,
        feedback_note: Annotated[str | None, Field(max_length=1000, description='digital: where the observations come from.')] = None,
        horizon_days: Annotated[int, Field(ge=7, le=365, description='Days simulated by compartmental, agents, digital.')] = 180,
        peer_effect: Annotated[float, Field(ge=0, le=1, description='agents: peer influence.')] = 0.08,
        media_effect: Annotated[float, Field(ge=0, le=1, description='agents: media influence.')] = 0.05,
        priors: Annotated[dict[str, float] | None, Field(description='bayes, optional: trust_a, trust_b, barrier_a, barrier_b '
            '(Beta priors; defaults 6, 4, 4, 6).')] = None,
        regional_mode: Literal['isolated', 'grouped'] = 'isolated',
        regional_target: Literal['barrier', 'trust', 'diffusion'] = 'barrier',
        audience: Literal['households', 'health_workers', 'community_leaders', 'policy_makers'] = 'households',
        tone: Literal['clear', 'warm', 'formal'] = 'clear',
        apply_to_twin: Annotated[bool, Field(description='inoculation: also re-run the digital twin with the estimated '
            'message strength. Only if the researcher asks for it.')] = False,
    ) -> dict:
        """Run one journey stage (4-13) after the researcher agreed to continue. Stages must go in order.

        Order: encoding, compartmental, agents, digital (researcher's field observations), bayes, rl, regional
        (optional), graph, inoculation, policy (researcher approves the export). Re-running a stage clears the later
        stages that read it."""
        body = {'horizon_days': horizon_days, 'peer_effect': peer_effect, 'media_effect': media_effect,
                'regional_mode': regional_mode, 'regional_target': regional_target, 'audience': audience, 'tone': tone,
                'apply_to_twin': apply_to_twin}
        optional = {'approval_statement': approval_statement, 'observed_adoption': observed_adoption,
                    'trust_shift': trust_shift, 'barrier_shift': barrier_shift, 'observed_series': observed_series,
                    'feedback_note': feedback_note, 'priors': priors}
        body |= {key: value for key, value in optional.items() if value is not None}
        return await journey_call('POST', workspace_id, journey_id, f'/stages/{stage}', json=body, audit_fields={
            'tool': 'ndim_journey_run_stage', 'stage': stage, 'approval_statement': approval_statement} if approval_statement else None)

    return mcp


__all__ = ['EngineError', 'create_server']
