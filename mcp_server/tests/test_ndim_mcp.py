"""Offline tests: the engine is replaced by httpx.MockTransport, so no server is needed."""
import asyncio
import json

import httpx
import pytest
from mcp.server.fastmcp.exceptions import ToolError

from ndim_mcp.client import EngineClient, EngineError, check_ids
from ndim_mcp.config import Settings
from ndim_mcp.server import create_server
from ndim_mcp.summaries import (
    compare_runs,
    summarize_plan,
    summarize_run,
    trajectory_stats,
)

WS = 'ndim-core'
RID = '6ffa464d-3557-4be5-b0fc-78089d63c948'
RID2 = '370898ca-5974-4cc5-912f-b408c3f6c847'


def trajectory(final, days=10):
    return [{'day': float(d), 'adoption': final * (d + 1) / days, 'adoption_lower': 0.0, 'adoption_upper': 1.0,
             **{c: 0.2 for c in 'SMTIR'}} for d in range(days)]


def make_run(run_id=RID, status='completed', influence=0.38, strength=0.5, base_final=0.7, alt_final=0.9,
             sha='a' * 64, code='sha256:' + 'c' * 64, model='compartmental'):
    plan = [{'id': 'encode', 'tool': 'encode', 'title': 'Encode'}, {'id': 'baseline', 'tool': 'simulate', 'title': 'B', 'strength': 0.0},
            {'id': 'intervention', 'tool': 'simulate', 'title': 'I', 'strength': strength},
            {'id': 'check', 'tool': 'check', 'title': 'Check'}, {'id': 'brief', 'tool': 'brief', 'title': 'Brief'}]
    outputs = {}
    if status == 'completed':
        outputs = {'encode': {'trust_score': 0.6, 'adoption_barrier_score': 0.7, 'themes': ['cost'], 'reviewer_notes': 'x' * 900},
                   'baseline': {'parameters': {'intervention_strength': 0.0, 'trust_score': 0.6}, 'model': model,
                                'trajectory': trajectory(base_final), 'method_status': 'illustrative_uncalibrated'},
                   'intervention': {'parameters': {'intervention_strength': strength, 'trust_score': 0.6}, 'model': model,
                                    'trajectory': trajectory(alt_final), 'method_status': 'illustrative_uncalibrated'},
                   'check': {'passed': True, 'checks': [], 'interpretation': 'Numerical consistency only.'},
                   'brief': {'markdown': '# brief'}}
    return {'run_id': run_id, 'workspace_id': WS, 'status': status, 'title': 'Does it work?', 'skill': 'scenario',
            'plan': plan, 'outputs': outputs, 'events': [{'type': 'planned', 'message': 'm'}], 'review': None,
            'warnings': ['limits'], 'blockers': [],
            'request': {'model': model, 'horizon_days': 90, 'intervention_strength': strength, 'initial_adoption': 0.1,
                        'narrative_influence': influence, 'language': 'en', 'consent': 'synthetic', 'profile': 'auto'},
            'execution': {'sensitivity_grid': [], 'profile': 'balanced'},
            'provenance': {'source_sha256': sha, 'code_version': code, 'planner': 'p'}}


def build(handler, **settings):
    cfg = Settings(audit_log=None, retry_base_delay=0, **settings)
    client = EngineClient(cfg, transport=httpx.MockTransport(handler))
    return create_server(cfg, client)


def call(server, name, **args):
    async def run():
        return await server.call_tool(name, args)
    result = asyncio.run(run())
    if isinstance(result, tuple):  # (content blocks, structured content)
        return result[1]
    if isinstance(result, list):  # content blocks only: the payload is JSON text
        return json.loads(result[0].text)
    return result


def test_trajectory_stats_reports_peak_and_band():
    stats = trajectory_stats(trajectory(0.9))
    assert stats['final_adoption'] == 0.9 and stats['peak_day'] == 9.0 and stats['points'] == 10
    assert stats['final_heuristic_band'] == [0.0, 1.0]


def test_summary_drops_long_text_and_trajectories_by_default():
    summary = summarize_run(make_run())
    assert 'reviewer_notes' not in summary['encoding']
    assert all('trajectory' not in sim for sim in summary['simulations'])
    assert summary['comparison']['baseline_vs_intervention']['delta_final_adoption'] == 0.2
    assert 'not an estimated treatment effect' in summary['comparison']['baseline_vs_intervention']['note']
    assert 'trajectory' in summarize_run(make_run(), include_trajectories=True)['simulations'][0]


def test_summary_of_failed_run_points_to_resume_not_approval():
    summary = summarize_run(make_run(status='failed'))
    assert 'ndim_resume_experiment' in summary['next'] and summary['brief_available'] is False


def test_plan_summary_requires_researcher_approval_and_flags_blockers():
    run = make_run(status='planned')
    assert 'explicit approval' in summarize_plan(run)['next']
    run['blockers'] = ['English only']
    assert summarize_plan(run)['next'].startswith('BLOCKED')


def test_compare_is_controlled_only_when_one_factor_varies_on_same_evidence():
    ok = compare_runs([make_run(RID, influence=0.2), make_run(RID2, influence=0.6)])
    assert ok['comparability'] == {'varied_factors': ['narrative_influence'], 'notes': [], 'controlled': True,
                                   'reference_run_id': None}
    mixed = compare_runs([make_run(RID, influence=0.2), make_run(RID2, influence=0.6, strength=0.9)])
    assert mixed['comparability']['controlled'] is False and 'More than one factor' in mixed['comparability']['notes'][0]
    other_evidence = compare_runs([make_run(RID, influence=0.2), make_run(RID2, influence=0.6, sha='b' * 64)])
    assert other_evidence['comparability']['controlled'] is False
    other_code = compare_runs([make_run(RID, influence=0.2), make_run(RID2, influence=0.6, code='sha256:' + 'd' * 64)])
    assert any('code versions' in note for note in other_code['comparability']['notes'])


def test_compare_excludes_unfinished_runs():
    result = compare_runs([make_run(RID), make_run(RID2, status='failed')])
    assert [row['run_id'] for row in result['rows']] == [RID]
    assert result['excluded'][0]['run_id'] == RID2 and result['comparability']['controlled'] is False


def test_compare_delta_matches_run_summary():
    run = make_run(base_final=0.78713, alt_final=0.89744)
    assert compare_runs([run])['rows'][0]['delta_final_adoption'] == \
        summarize_run(run)['comparison']['baseline_vs_intervention']['delta_final_adoption']


@pytest.mark.parametrize('workspace,run_id', [('../etc', RID), ('Bad Slug', RID), (WS, '../../x'), (WS, 'not-a-uuid'), (WS, RID + '/start')])
def test_ids_are_validated_before_use_in_a_url(workspace, run_id):
    with pytest.raises(EngineError):
        check_ids(workspace, run_id)


def test_start_records_approval_and_retries_when_queue_full(tmp_path):
    seen = {'starts': 0}
    audit_file = tmp_path / 'audit.jsonl'

    def handler(request):
        if request.method == 'POST' and request.url.path.endswith('/start'):
            seen['starts'] += 1
            return httpx.Response(429, json={'detail': 'queue full'}) if seen['starts'] < 3 else httpx.Response(200, json={})
        return httpx.Response(200, json=make_run())
    cfg = Settings(audit_log=audit_file, retry_base_delay=0)
    server = create_server(cfg, EngineClient(cfg, transport=httpx.MockTransport(handler)))
    body = call(server, 'ndim_start_experiment', workspace_id=WS, run_id=RID, approval_statement='Approved, please run it.')
    assert seen['starts'] == 3 and body['status'] == 'completed'
    entry = json.loads(audit_file.read_text().splitlines()[0])
    assert entry['approval_statement'] == 'Approved, please run it.' and entry['run_id'] == RID


def test_start_without_real_approval_never_reaches_the_engine():
    calls = []
    server = build(lambda request: calls.append(request) or httpx.Response(200, json={}))
    with pytest.raises(ToolError, match='approval_statement'):
        call(server, 'ndim_start_experiment', workspace_id=WS, run_id=RID, approval_statement='ok')
    assert calls == []


def test_engine_error_detail_is_surfaced_to_the_agent():
    server = build(lambda request: httpx.Response(422, json={'detail': [{'loc': ['body', 'evidence'], 'msg': 'too short'}]}))
    with pytest.raises(Exception, match='evidence: too short'):
        call(server, 'ndim_plan_experiment', workspace_id=WS, question='A long enough question', evidence='x' * 30)


def test_unreachable_engine_gives_actionable_message():
    def handler(request):
        raise httpx.ConnectError('refused')
    with pytest.raises(Exception, match='Cannot reach the NDIM engine'):
        call(build(handler), 'ndim_list_workspaces')


def test_status_does_not_leak_local_paths():
    def handler(request):
        if request.url.path == '/health':
            return httpx.Response(200, json={'status': 'ok', 'local_storage': {'paths': {'data': '/home/secret'}}})
        return httpx.Response(200, json={'resources': {k: 1 for k in ('cpu_available', 'memory_available_mb', 'recommended_profile',
                                                                       'worker_limit', 'profiles', 'dependencies')},
                                          'planner': 'p', 'implemented': [], 'unavailable': ['x'], 'access': 'a'})
    assert '/home/secret' not in json.dumps(call(build(handler), 'ndim_engine_status'))


def test_dangerous_tools_are_not_exposed():
    names = {tool.name for tool in asyncio.run(build(lambda r: httpx.Response(200, json={})).list_tools())}
    assert not {n for n in names if any(word in n for word in ('delete', 'review', 'approve'))}
    assert 'ndim_start_experiment' in names


# ---- sweeps -----------------------------------------------------------------------------------

from ndim_mcp import sweeps

BASE = {'narrative_influence': 0.38, 'initial_adoption': 0.1, 'intervention_strength': 0.3, 'horizon_days': 90}


def test_one_at_a_time_design_has_base_run_first_and_skips_base_values():
    runs = sweeps.design(BASE, {'narrative_influence': [0.2, 0.38, 0.6]}, 'one_at_a_time')
    assert [r['label'] for r in runs] == ['base', 'narrative_influence=0.2', 'narrative_influence=0.6']
    assert runs[1]['values'] == BASE | {'narrative_influence': 0.2}


def test_grid_design_is_cartesian_and_capped():
    assert len(sweeps.design(BASE, {'narrative_influence': [0.2, 0.6], 'intervention_strength': [0.1, 0.5, 0.9]}, 'grid')) == 6
    with pytest.raises(ValueError, match='limit is 24'):
        sweeps.design(BASE, {'narrative_influence': [i / 10 for i in range(5)], 'initial_adoption': [i / 10 for i in range(6)]}, 'grid')


@pytest.mark.parametrize('vary,message', [({}, 'at least one'), ({'trust_score': [0.5]}, 'Cannot vary'),
                                          ({'narrative_influence': [1.5]}, 'between'), ({'narrative_influence': [0.2, 0.2]}, 'distinct'),
                                          ({'horizon_days': [10.5]}, 'whole days'), ({'horizon_days': [3]}, 'between')])
def test_design_rejects_bad_input(vary, message):
    with pytest.raises(ValueError, match=message):
        sweeps.design(BASE, vary, 'one_at_a_time')


def test_reference_mode_treats_one_at_a_time_design_as_controlled():
    runs = [make_run(RID, influence=0.38), make_run(RID2, influence=0.6),
            make_run('11111111-1111-4111-8111-111111111111', influence=0.38, strength=0.9)]
    without = compare_runs(runs)
    assert without['comparability']['controlled'] is False
    with_ref = compare_runs(runs, reference_id=RID)
    assert with_ref['comparability']['controlled'] is True and with_ref['comparability']['reference_run_id'] == RID
    assert with_ref['rows'][1]['varied_vs_reference'] == ['narrative_influence']
    two = compare_runs([make_run(RID, influence=0.38), make_run(RID2, influence=0.6, strength=0.9)], reference_id=RID)
    assert two['comparability']['controlled'] is False and 'more than one factor' in two['comparability']['notes'][0]


class FakeEngine:
    """Minimal stand-in: plans store the request; start marks complete; queue rejects the first start of run 2."""

    def __init__(self):
        self.runs, self.plans, self.rejected = {}, [], False

    def __call__(self, request):
        path, body = request.url.path, (json.loads(request.content) if request.content else None)
        if request.method == 'POST' and path == '/engine/plans':
            run_id = f'{len(self.runs):08d}-0000-4000-8000-000000000000'
            run = make_run(run_id, status='planned', influence=body['narrative_influence'], strength=body['intervention_strength'])
            run['request'] |= {'horizon_days': body['horizon_days'], 'initial_adoption': body['initial_adoption']}
            run['provenance']['source_sha256'] = __import__('hashlib').sha256(body['evidence'].encode()).hexdigest()
            self.runs[run_id] = run
            self.plans.append(body)
            return httpx.Response(201, json=run)
        run_id = path.split('/runs/')[1].split('/')[0]
        if request.method == 'POST' and path.endswith('/start'):
            if run_id.startswith('00000002') and not self.rejected:
                self.rejected = True
                return httpx.Response(429, json={'detail': 'queue full'})
            done = make_run(run_id, influence=self.runs[run_id]['request']['narrative_influence'],
                            strength=self.runs[run_id]['request']['intervention_strength'])
            done['request'] = self.runs[run_id]['request']
            done['provenance'] = self.runs[run_id]['provenance']
            self.runs[run_id] = done
            return httpx.Response(200, json=done)
        return httpx.Response(200, json=self.runs[run_id])


def test_plan_sweep_sends_identical_evidence_and_scenario_workflow():
    fake = FakeEngine()
    body = call(build(fake), 'ndim_plan_sweep', workspace_id=WS, question='How does influence matter?', evidence='e' * 40,
                vary={'narrative_influence': [0.2, 0.6]}, consent='synthetic')
    assert body['n_runs'] == 3 and body['reference_run_id'] == body['planned'][0]['run_id']
    assert {plan['evidence'] for plan in fake.plans} == {'e' * 40} and {plan['skill'] for plan in fake.plans} == {'scenario'}
    assert 'explicit approval' in body['next']


def test_plan_sweep_stops_at_first_blocker():
    def handler(request):
        run = make_run(status='planned')
        run['blockers'] = ['Supply an English source.']
        return httpx.Response(201, json=run)
    body = call(build(handler), 'ndim_plan_sweep', workspace_id=WS, question='How does influence matter?', evidence='e' * 40,
                vary={'narrative_influence': [0.2, 0.6]}, language='rw')
    assert body['blocked'] is True and len(body['planned']) == 1 and body['next'].startswith('BLOCKED')


def test_run_sweep_starts_all_retries_queue_and_compares(tmp_path):
    fake = FakeEngine()
    audit_file = tmp_path / 'audit.jsonl'
    cfg = Settings(audit_log=audit_file, retry_base_delay=0)
    server = create_server(cfg, EngineClient(cfg, transport=httpx.MockTransport(fake)))
    plan = call(server, 'ndim_plan_sweep', workspace_id=WS, question='How does influence matter?', evidence='e' * 40,
                vary={'narrative_influence': [0.2, 0.6]}, consent='synthetic')
    ids = [item['run_id'] for item in plan['planned']]
    body = call(server, 'ndim_run_sweep', workspace_id=WS, run_ids=ids, approval_statement='Approved: run the whole design.',
                reference_run_id=plan['reference_run_id'])
    assert fake.rejected and body['errors'] == [] and body['still_running'] == []
    assert body['comparison']['comparability']['controlled'] is True and len(body['comparison']['rows']) == 3
    logged = [json.loads(line)['run_id'] for line in audit_file.read_text().splitlines()]
    assert sorted(logged) == sorted(ids)


def test_run_sweep_keeps_going_when_one_run_cannot_start():
    fake = FakeEngine()
    server = build(fake)
    ids = [item['run_id'] for item in call(server, 'ndim_plan_sweep', workspace_id=WS, question='How does influence matter?',
                                           evidence='e' * 40, vary={'narrative_influence': [0.2, 0.6]})['planned']]
    original = fake.__call__

    def handler(request):
        if request.url.path.endswith(f'{ids[1]}/start'):
            return httpx.Response(409, json={'detail': 'not eligible'})
        return original(request)
    server = build(handler)
    body = call(server, 'ndim_run_sweep', workspace_id=WS, run_ids=ids, approval_statement='Approved: run the whole design.')
    assert body['errors'][0]['run_id'] == ids[1] and '409' in body['errors'][0]['error']
    # A run that could not start is reported once, in errors, and is not compared.
    assert body['comparison']['excluded'] == []
    assert ids[1] not in [row['run_id'] for row in body['comparison']['rows']] and len(body['comparison']['rows']) == 2
