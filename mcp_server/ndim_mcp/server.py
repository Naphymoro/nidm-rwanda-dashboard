"""FastMCP server. Agents propose and read; only the engine's allowlisted tools produce scientific results.

Deliberately not exposed: deleting runs, saving researcher review notes, creating or editing workspaces, and
lesson answers. Those are researcher decisions or destructive, so they stay in the engine UI.
"""
import asyncio
import time
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from . import audit, sweeps
from .client import EngineClient, EngineError, check_ids
from .config import Settings
from .summaries import NOTICE, TERMINAL, compare_runs, summarize_plan, summarize_run

INSTRUCTIONS = """NDIM scientific engine: a deterministic digital twin of narrative diffusion and adoption.
Workflow: ndim_engine_status -> ndim_list_workspaces -> ndim_plan_experiment -> SHOW THE PLAN TO THE RESEARCHER AND GET
THEIR APPROVAL -> ndim_start_experiment -> ndim_wait_for_run / ndim_get_run -> ndim_get_brief.
Parameter sweeps: ndim_plan_sweep -> researcher approval -> ndim_run_sweep (runs and compares server-side).
Results are illustrative and uncalibrated. Never present them as forecasts or validated findings. Never approve a plan
or write a review on the researcher's behalf."""

READ = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)

Workspace = Annotated[str, Field(description='Workspace slug from ndim_list_workspaces, e.g. "ndim-core".')]
RunId = Annotated[str, Field(description='Run UUID returned by ndim_plan_experiment.')]
Approval = Annotated[str, Field(min_length=12, max_length=1000, description=(
    "The researcher's own words approving THIS plan, quoted from the conversation. Only call this tool after the "
    'researcher has actually approved; never write this text yourself. It is stored in an audit log.'))]


def create_server(settings=None, client=None, host='127.0.0.1', port=8000):
    settings = settings or Settings.from_env()
    engine = client or EngineClient(settings)
    mcp = FastMCP('ndim-engine', instructions=INSTRUCTIONS, host=host, port=port)

    async def fetch_run(workspace_id, run_id):
        check_ids(workspace_id, run_id)
        return await engine.request('GET', f'/engine/workspaces/{workspace_id}/runs/{run_id}')

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
        """Return the engine's teaching lessons and its synthetic sample field notes.

        The sample is synthetic and safe for smoke-testing a pipeline (use consent="synthetic"). It is not real data."""
        return await engine.request('GET', '/engine/lessons')

    @mcp.tool(annotations=WRITE)
    async def ndim_plan_experiment(
        workspace_id: Workspace,
        question: Annotated[str, Field(min_length=8, max_length=1000, description='The research question, in words. '
            'Keywords steer the workflow: "sensitivity"/"sweep" -> intervention-strength sweep; "scenario"/"compare"/'
            '"intervention"/"what if" -> baseline vs intervention; otherwise evidence-only.')],
        evidence: Annotated[str, Field(min_length=20, max_length=20000, description='Source narrative or field notes, in '
            'English. Non-English text is blocked by the engine; supply an explicit translation.')],
        consent: Annotated[Literal['synthetic', 'research_use', 'unconfirmed'], Field(description=(
            '"research_use" only if the researcher confirmed permission to use this evidence; "synthetic" for demo data; '
            'otherwise "unconfirmed". Never upgrade this yourself.'))] = 'unconfirmed',
        skill: Annotated[Literal['auto', 'evidence', 'scenario', 'sensitivity'], Field(description='Workflow. "auto" infers it from the question.')] = 'auto',
        model: Annotated[Literal['compartmental', 'agent_based', 'hybrid'], Field(description='Model family. agent_based ignores '
            'intervention strength, so it is blocked for scenario and sensitivity workflows.')] = 'compartmental',
        profile: Annotated[Literal['auto', 'economy', 'balanced', 'thorough'], Field(description='Sensitivity grid density: 3, 7 or 11 points.')] = 'auto',
        horizon_days: Annotated[int, Field(ge=7, le=365)] = 90,
        intervention_strength: Annotated[float, Field(ge=0, le=1)] = 0.3,
        initial_adoption: Annotated[float, Field(ge=0, le=1)] = 0.1,
        narrative_influence: Annotated[float, Field(ge=0, le=1)] = 0.38,
        language: Annotated[Literal['en', 'rw', 'fr', 'other'], Field(description='Language of the evidence text.')] = 'en',
        expertise: Annotated[Literal['guided', 'researcher', 'expert'], Field(description='Explanation level stored with the run.')] = 'guided',
        source_name: Annotated[str, Field(min_length=1, max_length=240)] = 'Researcher-supplied field note',
        prior_run_ids: Annotated[list[str] | None, Field(max_length=3, description='Completed runs that carry a researcher review, '
            'used as context only; they never change model parameters.')] = None,
    ) -> dict:
        """Create a reviewable experiment plan. Nothing executes until ndim_start_experiment.

        Returns the steps, warnings and any blockers. Present them to the researcher before asking for approval."""
        check_ids(workspace_id)
        prior_run_ids = prior_run_ids or []
        for prior in prior_run_ids:
            check_ids(workspace_id, prior)
        payload = {'workspace_id': workspace_id, 'question': question, 'evidence': evidence, 'consent': consent,
                   'skill': skill, 'model': model, 'profile': profile, 'horizon_days': horizon_days,
                   'intervention_strength': intervention_strength, 'initial_adoption': initial_adoption,
                   'narrative_influence': narrative_influence, 'language': language, 'expertise': expertise,
                   'source_name': source_name, 'prior_run_ids': prior_run_ids}
        return summarize_plan(await engine.request('POST', '/engine/plans', json=payload))

    async def gated(tool, action, workspace_id, run_id, approval_statement, wait_seconds):
        check_ids(workspace_id, run_id)
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
        """List a workspace's runs, newest first as the engine orders them."""
        check_ids(workspace_id)
        return await engine.request('GET', f'/engine/workspaces/{workspace_id}/runs', params={'offset': offset, 'limit': limit})

    @mcp.tool(annotations=READ)
    async def ndim_get_brief(workspace_id: Workspace, run_id: RunId) -> dict:
        """Return the engine-generated research brief (Markdown) for a completed run, marked as an exploratory draft."""
        check_ids(workspace_id, run_id)
        markdown = await engine.request('GET', f'/engine/workspaces/{workspace_id}/runs/{run_id}/artifacts/brief', text=True)
        return {'run_id': run_id, 'markdown': markdown, 'notice': NOTICE}

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
        question: Annotated[str, Field(min_length=8, max_length=1000)],
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
                'next': 'Show this design to the researcher and obtain explicit approval before calling ndim_run_sweep '
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
        for run_id in unique:
            audit.record(settings, 'ndim_run_sweep', workspace_id=workspace_id, run_id=run_id, approval_statement=approval_statement)
        gate = asyncio.Semaphore(4)
        errors = []

        async def begin(run_id):
            async with gate:
                try:
                    await engine.request('POST', f'/engine/workspaces/{workspace_id}/runs/{run_id}/start', retry_busy=True)
                    return run_id
                except EngineError as exc:
                    errors.append({'run_id': run_id, 'error': str(exc)})

        started = [run_id for run_id in await asyncio.gather(*(begin(run_id) for run_id in unique)) if run_id]
        finished = await asyncio.gather(*(wait(workspace_id, run_id, wait_seconds) for run_id in started))
        return {'comparison': compare_runs(list(finished), reference_id=reference_run_id), 'errors': errors,
                'still_running': [run['run_id'] for run in finished if run['status'] not in TERMINAL],
                'next': 'Report with the comparability notes. If runs are still running, call ndim_wait_for_run '
                        'then ndim_compare_runs.'}

    return mcp


__all__ = ['EngineError', 'create_server']
