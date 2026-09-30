"""Offline tests: the engine is replaced by httpx.MockTransport, so no server is needed."""
import asyncio
import json
import re

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


def curve(*levels):
    return [{'day': float(day), 'adoption': level} for day, level in enumerate(levels)]


def test_trajectory_stats_reports_endpoints_and_band():
    stats = trajectory_stats(trajectory(0.9))
    assert stats['final_adoption'] == 0.9 and stats['points'] == 10
    assert stats['final_heuristic_band'] == [0.0, 1.0]


def test_rising_curve_has_no_peak_only_fastest_growth():
    # A live chat reported the last day as the "peak": for adoption that only rises, max() is the endpoint restated.
    stats = trajectory_stats(curve(0.1, 0.2, 0.5, 0.7, 0.8))
    assert stats['shape'] == 'rises_to_end' and 'peak_day' not in stats and 'peak_adoption' not in stats
    assert stats['fastest_growth_day'] == 2.0 and stats['fastest_growth'] == 0.3


def test_plateau_that_only_differs_below_reporting_precision_is_not_a_peak():
    stats = trajectory_stats(curve(0.1, 0.5, 0.9, 0.900001, 0.9000004))
    assert stats['shape'] == 'rises_to_end' and 'peak_day' not in stats


def test_curve_that_falls_before_the_end_reports_its_peak():
    stats = trajectory_stats(curve(0.1, 0.4, 0.6, 0.5, 0.45))
    assert stats['shape'] == 'peaks_before_end' and stats['peak_day'] == 2.0 and stats['peak_adoption'] == 0.6
    assert stats['fastest_growth_day'] == 1.0


def test_flat_and_single_point_curves_report_no_peak_or_growth():
    for levels in [(0.3, 0.3, 0.3), (0.3,)]:
        stats = trajectory_stats(curve(*levels))
        assert stats['shape'] == 'flat' and 'peak_day' not in stats and 'fastest_growth_day' not in stats


def test_fastest_growth_ties_resolve_to_the_first_day():
    assert trajectory_stats(curve(0.0, 0.25, 0.5, 0.75))['fastest_growth_day'] == 1.0


def test_compare_does_not_show_the_last_day_as_a_peak():
    result = compare_runs([make_run(RID)])
    row = result['rows'][0]
    assert row['shape'] == 'rises_to_end' and row['peak_day'] is None and row['fastest_growth_day'] is not None
    header, _, line = result['markdown_table'].splitlines()
    cells = dict(zip(header.strip('| ').split(' | '), line.strip('| ').split(' | ')))
    assert cells['shape'] == 'rises_to_end' and cells['peak_day'] == ''


def test_scenario_plan_states_the_intervention_mapping_before_approval():
    # A live chat asked for approval without saying that "more trained CHWs" is only an abstract 0-1 number.
    plan = summarize_plan(make_run(status='planned', strength=0.3))
    assert 'intervention_strength = 0.3' in plan['intervention_mapping'] and 'Does it work?' in plan['intervention_mapping']
    assert 'Before asking for approval' in plan['next'] and 'intervention_mapping' in plan['next']
    assert plan['next'].index('intervention_mapping') < plan['next'].index('explicit approval')


def test_question_must_be_verbatim_and_shown_back_before_approval():
    # A live agent planned "adoption of gas stoves" for a question about "clean cooking adoption".
    tools = {t.name: t for t in asyncio.run(build(lambda r: httpx.Response(200, json={})).list_tools())}
    for name in ('ndim_plan_experiment', 'ndim_plan_sweep'):
        description = tools[name].inputSchema['properties']['question']['description']
        assert 'verbatim' in description and 'gas stoves' in description, name
    next_step = summarize_plan(make_run(status='planned'))['next']
    assert 'quoting the question field exactly' in next_step
    assert next_step.index('question') < next_step.index('explicit approval')


def test_plan_sweep_echoes_the_question_for_the_researcher_to_check():
    body = call(build(FakeEngine()), 'ndim_plan_sweep', workspace_id=WS, question='How does influence matter?',
                evidence='e' * 40, vary={'narrative_influence': [0.2, 0.6]})
    assert body['question'] == 'How does influence matter?' and 'quoting the question exactly' in body['next']


def test_sensitivity_plan_mapping_lists_the_grid_and_evidence_plan_has_none():
    run = make_run(status='planned', strength=0.3)
    run['skill'], run['execution']['sensitivity_grid'] = 'sensitivity', [0.0, 0.5, 1.0]
    assert 'plus a grid of 0, 0.5, 1' in summarize_plan(run)['intervention_mapping']
    run['skill'] = 'evidence'
    plan = summarize_plan(run)
    assert plan['intervention_mapping'] is None and 'intervention_mapping' not in plan['next']


def test_scenario_comparison_carries_a_quotable_non_causal_headline():
    headline = summarize_run(make_run(base_final=0.82693, alt_final=0.88651))['comparison']['baseline_vs_intervention']['headline']
    assert 'day 9 ' in headline and '0.8269 in the baseline arm' in headline and '0.8865 in the intervention arm' in headline
    assert '+0.0596 (+5.96 percentage points)' in headline and 'not an estimated effect' in headline
    conclusion = summarize_run(make_run())['comparison']['baseline_vs_intervention']['conclusion']
    assert 'cannot say whether the intervention would change real adoption' in conclusion


def test_completed_scenario_spells_out_the_sentences_to_copy():
    # Agents told to quote a field by name paraphrased it; the sentences themselves must be in the instruction.
    summary = summarize_run(make_run())
    pair = summary['comparison']['baseline_vs_intervention']
    next_step = summary['next']
    assert f'"{pair["headline"]}"' in next_step and f'"{pair["conclusion"]}"' in next_step
    assert next_step.index(pair['headline']) < next_step.index(pair['conclusion']) < next_step.index('When reporting')


def test_run_without_a_scenario_comparison_copies_only_the_evidence_sentence():
    run = make_run()
    run['plan'] = [step for step in run['plan'] if step['id'] != 'intervention']
    del run['outputs']['intervention']
    next_step = summarize_run(run)['next']
    assert 'Open your report' not in next_step and 'End your report' not in next_step
    assert 'First report the evidence signals' in next_step and 'character for character' not in next_step


def test_evidence_signals_sentence_names_the_scores_and_their_limits():
    # Live reports led with the headline and skipped the encoded inputs that explain it.
    run = make_run()
    run['outputs']['diagnose'] = {'misinformation_risk_score': 0.12, 'threat_type': 'affordability_fear'}
    signals = summarize_run(run)['evidence_signals']
    assert signals.startswith('The keyword heuristic scored this narrative 0.600 on trust and 0.700 on adoption barriers')
    assert 'misinformation risk 0.120 (flagged threat: affordability fear, pending human review)' in signals
    assert 'Themes found: cost.' in signals and 'not from measurements in a community' in signals


def test_evidence_signals_sit_between_headline_and_conclusion():
    summary = summarize_run(make_run())
    pair, next_step = summary['comparison']['baseline_vs_intervention'], summary['next']
    assert next_step.index(pair['headline']) < next_step.index(summary['evidence_signals']) < next_step.index(pair['conclusion'])


def test_no_evidence_sentence_before_encoding_has_run():
    run = make_run(status='running')
    assert summarize_run(run).get('evidence_signals') is None and 'character for character' not in summarize_run(run)['next']


def test_reporting_rules_forbid_causal_verbs_and_recommendations():
    rules = summarize_run(make_run())['next']
    assert 'headline' in rules and 'close with its conclusion' in rules
    assert 'contributes to' in rules and 'not even with "may"' in rules
    assert 'no recommendations' in rules and 'never as a percent' in rules


def test_reporting_rules_forbid_calling_the_endpoint_a_peak():
    next_step = summarize_run(make_run())['next']
    assert 'fastest_growth_day' in next_step and 'peaks_before_end' in next_step


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
        return httpx.Response(200, json=make_run(status='completed' if seen['starts'] >= 3 else 'planned'))
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
        call(server, 'ndim_plan_experiment', workspace_id=WS, question='A long enough question', evidence='x' * 30, skill='evidence')


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


def test_plan_requires_an_explicit_workflow_and_describes_the_choice():
    # A live chat showed an agent that never read SKILL.md: it left the workflow to the planner and got "evidence"
    # for a "how might X change adoption" question. The rules it needs must be in what tools/list returns.
    calls = []
    server = build(lambda request: calls.append(request) or httpx.Response(201, json=make_run(status='planned')))
    with pytest.raises(ToolError, match='skill'):
        call(server, 'ndim_plan_experiment', workspace_id=WS, question='How might more CHWs change adoption?', evidence='e' * 40)
    assert calls == []
    tool = next(t for t in asyncio.run(server.list_tools()) if t.name == 'ndim_plan_experiment')
    skill = tool.inputSchema['properties']['skill']
    assert 'skill' in tool.inputSchema['required']
    assert 'scenario' in skill['description'] and 'change' in skill['description'] and 'auto' in skill['description']
    assert 'intervention_strength' in tool.description


SCENARIO = dict(workspace_id=WS, question='How might more CHWs change adoption?', evidence='e' * 40, skill='scenario')


def test_evidence_plan_has_no_strength_note():
    server = build(lambda request: httpx.Response(201, json=make_run(status='planned') | {'skill': 'evidence'}))
    plan = call(server, 'ndim_plan_experiment', **(SCENARIO | {'skill': 'evidence'}))
    assert plan['run_id'] == RID and 'Intervention strength' not in plan['next']


@pytest.mark.parametrize('strength,reason,expected,absent', [
    (0.3, None, 'Intervention strength 0.3 is the tool\'s default, described only as "moderate": an assumption, not '
                'derived from the evidence or measured from the intervention.', 'Reasoning given'),
    (0.7, 'they asked for "a strong push"', 'Intervention strength 0.7 is an assumption, not derived from the evidence or '
                'measured from the intervention. Reasoning given when planning: they asked for "a strong push".', "tool's default"),
])
def test_strength_note_explains_the_value_and_audit_log_keeps_the_reason(tmp_path, strength, reason, expected, absent):
    # Live agents never said why they used 0.3. Asked who chose it, one wrongly told the researcher it was their
    # choice, so the note states what is always true and asks the researcher to confirm.
    audit_file = tmp_path / 'audit.jsonl'
    cfg = Settings(audit_log=audit_file, retry_base_delay=0)
    server = create_server(cfg, EngineClient(cfg, transport=httpx.MockTransport(
        lambda request: httpx.Response(201, json=make_run(status='planned', strength=strength)))))
    args = {'intervention_strength': strength} | ({'strength_reason': reason} if reason else {})
    plan = call(server, 'ndim_plan_experiment', **SCENARIO, **args)
    assert expected in plan['intervention_mapping'] and absent not in plan['intervention_mapping']
    assert 'Confirm this value or give another before approving' in plan['intervention_mapping']
    assert "researcher's choice" not in plan['intervention_mapping']
    note = plan['intervention_mapping'][plan['intervention_mapping'].index('Intervention strength'):]
    assert f'copied character for character: "{note}"' in plan['next']
    assert plan['next'].index(note) < plan['next'].index('explicit approval')
    entry = json.loads(audit_file.read_text().splitlines()[0])
    assert entry['tool'] == 'ndim_plan_experiment' and entry['intervention_strength'] == strength
    assert entry['strength_reason'] == reason


def test_completed_run_and_brief_carry_reporting_rules():
    next_step = summarize_run(make_run())['next']
    assert 'never "adoption will reach' in next_step and 'never an effect' in next_step
    body = call(build(brief_engine), 'ndim_get_brief', workspace_id=WS, run_id=RID)
    assert 'Scope claims to this narrative' in body['reporting_rules']


def brief_engine(request):
    if request.url.path.endswith('/artifacts/brief'):
        return httpx.Response(200, text='# brief')
    return httpx.Response(200, json=make_run() | {'created_at': '2026-09-28T13:44:58.1+00:00'})


def test_brief_says_whose_run_it_is_and_carries_the_report_instructions():
    # A live agent answered a new question with an old run's brief, presented as a new result.
    body = call(build(brief_engine), 'ndim_get_brief', workspace_id=WS, run_id=RID)
    assert body['created_at'].startswith('2026-09-28') and body['question'] == 'Does it work?'
    assert f'This is run {RID}, created on 2026-09-28 13:44 UTC' in body['next']
    assert 'tell the researcher only that an earlier run exists' in body['next'] and 'Open your report with this sentence' in body['next']


def test_list_runs_marks_them_as_existing_work():
    listing = call(build(lambda request: httpx.Response(200, json={'runs': [], 'total': 0})), 'ndim_list_runs', workspace_id=WS)
    assert listing['total'] == 0 and 'plan a new experiment on their evidence' in listing['next']
    assert 'Never call ndim_start_experiment on a run you did not plan' in listing['next']


@pytest.mark.parametrize('tool,status,message', [
    ('ndim_start_experiment', 'completed', 'already completed'),
    ('ndim_start_experiment', 'failed', 'ndim_resume_experiment'),
    ('ndim_start_experiment', 'running', 'ndim_wait_for_run'),
    ('ndim_resume_experiment', 'completed', 'already completed'),
    ('ndim_resume_experiment', 'planned', 'cannot be resumed'),
])
def test_ineligible_run_is_refused_before_any_approval_is_logged(tmp_path, tool, status, message):
    # The audit log held an approval for "starting" an old completed run the engine then refused.
    audit_file, posts = tmp_path / 'audit.jsonl', []
    cfg = Settings(audit_log=audit_file, retry_base_delay=0)

    def handler(request):
        if request.method == 'POST':
            posts.append(request)
        return httpx.Response(200, json=make_run(status=status))
    server = create_server(cfg, EngineClient(cfg, transport=httpx.MockTransport(handler)))
    with pytest.raises(ToolError, match=message):
        call(server, tool, workspace_id=WS, run_id=RID, approval_statement='Yes, I approve this plan as shown.')
    assert posts == [] and not audit_file.exists()
    with pytest.raises(ToolError, match='no approval was recorded|No approval was recorded'):
        call(server, tool, workspace_id=WS, run_id=RID, approval_statement='Yes, I approve this plan as shown.')


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


def test_run_sweep_logs_no_approval_for_a_run_that_is_not_planned(tmp_path):
    fake = FakeEngine()
    audit_file = tmp_path / 'audit.jsonl'
    cfg = Settings(audit_log=audit_file, retry_base_delay=0)
    server = create_server(cfg, EngineClient(cfg, transport=httpx.MockTransport(fake)))
    ids = [item['run_id'] for item in call(server, 'ndim_plan_sweep', workspace_id=WS, question='How does influence matter?',
                                           evidence='e' * 40, vary={'narrative_influence': [0.2, 0.6]})['planned']]
    fake.runs[ids[1]] = make_run(ids[1], status='completed')
    body = call(server, 'ndim_run_sweep', workspace_id=WS, run_ids=ids, approval_statement='Approved: run the whole design.')
    assert body['errors'][0]['run_id'] == ids[1] and 'already completed' in body['errors'][0]['error']
    logged = [json.loads(line)['run_id'] for line in audit_file.read_text().splitlines()]
    assert ids[1] not in logged and sorted(logged) == sorted([ids[0], ids[2]])


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


# ---- tutorials for existing runs ---------------------------------------------------------------

LESSONS = {'lessons': [{'id': skill, 'number': number, 'title': title, 'subtitle': subtitle, 'duration': '12 min',
                        'skill': skill, 'question': 'q?'}
                       for skill, number, title, subtitle in (
                           ('evidence', '01', 'From story to evidence', 'Understand what a heuristic can and cannot tell you.'),
                           ('scenario', '02', 'Build a controlled comparison', 'Change one assumption. Inspect both trajectories.'),
                           ('sensitivity', '03', 'Test the assumptions', 'Explore sensitivity without mistaking it for uncertainty.'))],
           'sample': 'SYNTHETIC'}


def lessons_or(handler):
    def wrapped(request):
        if request.url.path == '/engine/lessons':
            return httpx.Response(200, json=LESSONS)
        return handler(request)
    return wrapped


def test_existing_runs_come_with_their_matching_tutorial():
    # The researcher's choice: an old run is met with the tutorial for its workflow, never with the old run itself.
    runs = {'runs': [{'run_id': RID, 'skill': 'scenario', 'title': 'Does it work?'},
                     {'run_id': RID2, 'skill': 'evidence', 'title': 'What is in it?'}], 'total': 2}
    listing = call(build(lessons_or(lambda request: httpx.Response(200, json=runs)), public_url='http://127.0.0.1:8010'),
                   'ndim_list_runs', workspace_id=WS)
    scenario, evidence = (row['matching_tutorial'] for row in listing['runs'])
    assert scenario['title'] == 'Lesson 02: Build a controlled comparison'
    assert scenario['link'] == 'http://127.0.0.1:8010/academy?workspace=ndim-core&lesson=scenario'
    assert evidence['lesson_id'] == 'evidence'
    assert 'Never present one as the answer' in listing['next'] and 'offer its matching_tutorial' in listing['next']
    assert all('run_id' not in row for row in listing['runs']), 'ids let agents fetch and present old results'


def test_brief_of_an_earlier_run_offers_the_tutorial_first():
    body = call(build(lessons_or(brief_engine)), 'ndim_get_brief', workspace_id=WS, run_id=RID)
    assert body['matching_tutorial']['lesson_id'] == 'scenario'
    assert 'do not present it or its brief as an answer' in body['next']
    assert body['next'].index('Build a controlled comparison') < body['next'].index('Open your report with this sentence')


def test_starting_a_completed_run_points_to_the_tutorial():
    with pytest.raises(ToolError, match='Build a controlled comparison'):
        call(build(lessons_or(lambda request: httpx.Response(200, json=make_run(status='completed')))),
             'ndim_start_experiment', workspace_id=WS, run_id=RID, approval_statement='Yes, I approve this plan as shown.')


def test_tutorial_offer_survives_an_engine_without_lessons():
    body = call(build(brief_engine), 'ndim_get_brief', workspace_id=WS, run_id=RID)  # /engine/lessons answers a run here
    assert body['matching_tutorial'] is None and 'plan a new experiment' in body['next']


def test_a_tutorial_can_be_planned_in_chat_with_its_lesson_id():
    sent = []

    def handler(request):
        sent.append(json.loads(request.content))
        return httpx.Response(201, json=make_run(status='planned'))
    call(build(handler), 'ndim_plan_experiment', workspace_id=WS, question='How does an intervention change adoption?',
         evidence='SYNTHETIC INTERVIEW SET for demonstration', skill='scenario', consent='synthetic', lesson_id='scenario')
    assert sent[0]['lesson_id'] == 'scenario'


# ---- the 13-stage journey ----------------------------------------------------------------------

JID = '0f5b1f7e-4c1a-4a7b-9a55-3d1c2e9b8a70'
STAGE_ROWS = [(1, 'intake', 'Narrative intake', 'Evidence', False), (2, 'gate', 'SDMX gate', 'Evidence', False),
              (3, 'repository', 'Repository', 'Evidence', True), (4, 'encoding', 'Encoding', 'Encode', False),
              (5, 'compartmental', 'Compartmental model', 'Model', False), (6, 'agents', 'Agent-based model', 'Model', False),
              (7, 'digital', 'Digital twin', 'Twin', True), (8, 'bayes', 'Bayesian update', 'Twin', False),
              (9, 'rl', 'RL optimizer', 'Twin', False), (10, 'regional', 'Regional analysis', 'Strategy', False),
              (11, 'graph', 'Knowledge graph', 'Strategy', False), (12, 'inoculation', 'Inoculation lab', 'Strategy', False),
              (13, 'policy', 'Policy output', 'Export', True)]


def journey_body(done=(), next_stage='intake', **extra):
    stages = [{'number': n, 'id': i, 'title': t, 'phase': p, 'researcher_decision': d, 'optional': i == 'regional',
               'status': 'done' if i in done else 'ready' if i == next_stage else 'waiting', 'needs': [], 'at': None}
              for n, i, t, p, d in STAGE_ROWS]
    record = {'record_id': RID2, 'admin_unit': 'Kicukiro / Niboye', 'source_name': 'Field team', 'period': '2026-Q2',
              'consent': 'research_use', 'excerpt': 'Households say...', 'review': None,
              'gate': {'gate': 'review_before_accepting', 'blockers': [], 'warnings': ['instruction-like text: review before accepting'],
                       'pii_flags': ['phone-or-id-like number'], 'quality_flags': []}}
    return {'journey_id': JID, 'workspace_id': WS, 'question': 'How might trusted messengers change clean cooking adoption?',
            'country': 'Rwanda', 'created_at': '2026-09-29T10:00:00+00:00', 'records': [record], 'stages': stages,
            'next_stage': next_stage, **extra}


def test_journey_view_asks_for_the_researcher_decision_on_each_record():
    view = call(build(lambda request: httpx.Response(200, json=journey_body(('intake', 'gate'), 'repository'))),
                'ndim_journey_status', workspace_id=WS, journey_id=JID)
    assert view['records'][0]['gate_flags'] == ['instruction-like text: review before accepting', 'phone-or-id-like number']
    assert 'ask the researcher to accept or reject each one' in view['next'] and 'Never decide for them' in view['next']
    assert ' 3. Repository (Evidence): ready [researcher decision]' in view['progress']
    assert 'Ask the researcher whether to continue before running it' in view['next']


def test_stage_result_is_compact_and_carries_its_limits_and_rules():
    output = {'model': 'compartmental', 'horizon_days': 10, 'method_status': 'illustrative_uncalibrated',
              'trajectory': trajectory(0.4), 'assumptions': {}, 'parameters': {'trust_score': 0.61234, 'barrier_score': 0.4,
                                                                            'narrative_influence': 0.3, 'intervention_strength': 0.2}}
    body = journey_body(('intake', 'gate', 'repository', 'encoding', 'compartmental'), 'agents', stage='compartmental', output=output)
    view = call(build(lambda request: httpx.Response(200, json=body)), 'ndim_journey_run_stage',
                workspace_id=WS, journey_id=JID, stage='compartmental')
    assert 'trajectory' not in json.dumps(view['result'])
    assert view['result']['stats']['shape'] == 'rises_to_end' and view['result']['inputs']['trust_score'] == 0.6123
    assert 'Not a forecast' in view['limits']
    assert 'Next stage: 6. Agent-based model.' in view['next'] and 'Write no recommendations' in view['next']


def test_rl_and_policy_are_never_presented_as_advice():
    rules = call(build(lambda request: httpx.Response(200, json=journey_body(stage='rl', output={
        'ranking': [], 'top_action': 'consumer_subsidy', 'formula': 'f', 'method': 'm', 'trust_used': 0.6, 'barrier_used': 0.4}))),
        'ndim_journey_run_stage', workspace_id=WS, journey_id=JID, stage='rl')
    assert 'not advice' in rules['limits'] and 'never present them as what to do' in rules['next']


def test_journey_decisions_are_audited_only_after_the_engine_accepts(tmp_path):
    audit_file = tmp_path / 'audit.jsonl'
    cfg = Settings(audit_log=audit_file, retry_base_delay=0)
    responses = [httpx.Response(409, json={'detail': 'Digital twin needs these stages first: Compartmental model.'}),
                 httpx.Response(200, json=journey_body(stage='digital', output={
                     'model': 'hybrid', 'horizon_days': 10, 'method_status': 'illustrative_uncalibrated',
                     'trajectory': trajectory(0.3), 'feedback': {'observed_adoption': 0.2}}))]
    server = create_server(cfg, EngineClient(cfg, transport=httpx.MockTransport(lambda request: responses.pop(0))))
    args = dict(workspace_id=WS, journey_id=JID, stage='digital', observed_adoption=0.2, trust_shift=0, barrier_shift=0,
                approval_statement='These are our June field numbers.')
    with pytest.raises(ToolError, match='needs these stages first'):
        call(server, 'ndim_journey_run_stage', **args)
    assert not audit_file.exists()
    call(server, 'ndim_journey_run_stage', **args)
    entry = json.loads(audit_file.read_text())
    assert entry['tool'] == 'ndim_journey_run_stage' and entry['stage'] == 'digital'
    assert entry['approval_statement'] == 'These are our June field numbers.'


def test_journey_stage_sends_only_what_the_researcher_gave():
    sent = []

    def handler(request):
        sent.append(json.loads(request.content))
        return httpx.Response(200, json=journey_body())
    call(build(handler), 'ndim_journey_run_stage', workspace_id=WS, journey_id=JID, stage='encoding')
    assert 'observed_adoption' not in sent[0] and 'approval_statement' not in sent[0]


def test_invalid_journey_id_never_reaches_a_url():
    paths = []

    def handler(request):
        paths.append(request.url.path)
        return httpx.Response(200, json={'journeys': []})
    with pytest.raises(ToolError, match='Invalid journey_id.*ndim_journey_list.*Do not start a new journey'):
        call(build(handler), 'ndim_journey_status', workspace_id=WS, journey_id='../x')
    assert paths == [f'/engine/workspaces/{WS}/journeys']


def test_a_mangled_journey_id_names_the_journey_it_meant():
    # A live agent dropped '-4a7b' from the UUID, then started a second journey and re-entered the evidence.
    rows = [{'journey_id': JID, 'question': 'How might trusted messengers change clean cooking adoption?',
             'created_at': '2026-09-29T10:00:00+00:00', 'updated_at': '2026-09-29T10:05:00+00:00', 'stages_done': 4}]
    server = build(lambda request: httpx.Response(200, json={'journeys': rows}))
    mangled = JID.replace('-4a7b', '')
    with pytest.raises(ToolError, match=f"Did you mean '{JID}'.*4 stage.*Do not start a new journey"):
        call(server, 'ndim_journey_run_stage', workspace_id=WS, journey_id=mangled, stage='compartmental')
    unknown = build(lambda request: httpx.Response(404, json={'detail': 'Journey not found'})
                    if request.url.path.endswith(JID) else httpx.Response(200, json={'journeys': rows}))
    with pytest.raises(ToolError, match=f"404.*Did you mean '{JID}'"):
        call(unknown, 'ndim_journey_status', workspace_id=WS, journey_id=JID)


def test_journey_start_describes_the_path_and_pins_the_id():
    view = call(build(lambda request: httpx.Response(201, json=journey_body())), 'ndim_journey_start',
                workspace_id=WS, question='How might trusted messengers change clean cooking adoption?',
                question_confirmation='Yes, that is my question.')
    assert view['next'].startswith(f'Use journey_id {JID} exactly')
    assert '6. Export: a policy draft of options' in view['next'] and '(stage 7)' in view['next'] and 'field notes' in view['next']
    # Given only phase names, a live agent called the twin "to validate findings" and the export "actionable".
    assert not re.search(r'\b(validat|actionable|calibrat)', view['next'].split('They decide')[0], re.I)


def test_compartments_come_with_the_engines_names():
    # Given only S/M/T/I/R, a live agent called M "Messenger" and I "Influenced".
    names = trajectory_stats(trajectory(0.5))['compartment_names']
    assert names['M'] == 'misinformed' and names['I'] == 'inoculated' and names['T'] == 'truth-aligned'


def test_journey_start_needs_the_researchers_confirmation_of_the_question(tmp_path):
    # A live agent started a journey for "... adoption in Rwanda?"; the researcher never saw the question it used.
    tools = {tool.name: tool for tool in asyncio.run(build(FakeEngine()).list_tools())}
    schema = tools['ndim_journey_start'].inputSchema
    assert 'question_confirmation' in schema['required'] and 'in Rwanda' in schema['properties']['question']['description']
    guide = {'stages': [{'number': n, 'id': i, 'title': t, 'phase': p, 'does': 'd', 'needs': [], 'researcher_decision': d}
                        for n, i, t, p, d in STAGE_ROWS], 'principles': []}
    view = call(build(lambda request: httpx.Response(200, json=guide)), 'ndim_journey_guide')
    assert view['intro'].count('\n- ') == 3 and '\n6. Export: a policy draft' in view['intro'] and '(stage 13)' in view['intro']
    assert view['next'].index('intro field word for word') < view['next'].index('show their question back in quotes') < view['next'].index(
        'question_confirmation')
    audit_file = tmp_path / 'audit.jsonl'
    cfg = Settings(audit_log=audit_file, retry_base_delay=0)
    server = create_server(cfg, EngineClient(cfg, transport=httpx.MockTransport(lambda request: httpx.Response(201, json=journey_body()))))
    call(server, 'ndim_journey_start', workspace_id=WS, question='How might trusted messengers change clean cooking adoption?',
         question_confirmation='Yes, that is my question.')
    entry = json.loads(audit_file.read_text())
    assert entry['tool'] == 'ndim_journey_start' and entry['journey_id'] == JID
    assert entry['question_confirmation'] == 'Yes, that is my question.'
