"""NIDM scientific harness: reviewable plans, bounded jobs and durable checkpoints.

One owning process per data directory is enforced with an SQLite exclusive lock.
Only allowlisted, deterministic scientific tools run here; no arbitrary code or
remote model calls. Browser disconnection does not cancel an approved job.
"""
import hashlib
import json
import logging
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator

from . import engine_store as store
from .engine_resources import resources, environment_manifest
from .engine_tools import execute_tool, fingerprint, LIMITS
from .engine_lessons import LESSONS, SAMPLE, public_lessons
from .storage import app_paths
from .workspaces import get_workspace

router = APIRouter(prefix='/engine', tags=['scientific-engine'])
ACTIVE = {'queued', 'running', 'cancelling'}
logger = logging.getLogger(__name__)


class ExperimentRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, allow_inf_nan=False)
    workspace_id: str = Field(pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$', max_length=160)
    question: str = Field(min_length=8, max_length=1000)
    evidence: str = Field(min_length=20, max_length=20000)
    skill: Literal['auto', 'evidence', 'scenario', 'sensitivity'] = 'auto'
    model: Literal['compartmental', 'agent_based', 'hybrid'] = 'compartmental'
    profile: Literal['auto', 'economy', 'balanced', 'thorough'] = 'auto'
    language: Literal['en', 'rw', 'fr', 'other'] = 'en'
    expertise: Literal['guided', 'researcher', 'expert'] = 'guided'
    source_name: str = Field(default='Researcher-supplied field note', min_length=1, max_length=240)
    consent: Literal['synthetic', 'research_use', 'unconfirmed'] = 'unconfirmed'
    horizon_days: int = Field(default=90, ge=7, le=365)
    intervention_strength: float = Field(default=.3, ge=0, le=1)
    initial_adoption: float = Field(default=.1, ge=0, le=1)
    narrative_influence: float = Field(default=.38, ge=0, le=1)
    lesson_id: Literal['evidence', 'scenario', 'sensitivity'] | None = None
    prior_run_ids: list[str] = Field(default_factory=list, max_length=3)
    # Groups experiments into one conversation in the chat UI; a run without one is its own thread.
    thread_id: str | None = Field(default=None, pattern=r'^[0-9a-f][0-9a-f-]{7,63}$')

    @model_validator(mode='after')
    def validate_meaningful_text(self):
        if not any(character.isalnum() for character in self.question):
            raise ValueError('Research question must contain words, not only punctuation or whitespace.')
        if not any(character.isalnum() for character in self.evidence):
            raise ValueError('Source evidence must contain readable words, not only punctuation or whitespace.')
        return self


class ReviewRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    note: str = Field(min_length=12, max_length=2000)


class LessonCheck(BaseModel):
    run_id: str
    choice: int = Field(ge=0, le=2)


def public(run):
    return {key: value for key, value in run.items() if key != 'outputs'} | {
        'outputs': run['outputs'], 'completed_steps': len(run['outputs']), 'total_steps': len(run['plan'])}


def build_plan(payload, resource_snapshot=None):
    workspace = get_workspace(payload.workspace_id)
    measured = resource_snapshot or resources()
    profile = measured['recommended_profile'] if payload.profile == 'auto' else payload.profile
    question = payload.question.lower()
    skill = payload.skill
    if skill == 'auto':
        skill = 'sensitivity' if any(word in question for word in ('sensitivity', 'sensitive', 'sweep')) else 'scenario' if any(word in question for word in ('scenario', 'compare', 'intervention', 'what if', 'adoption change')) else 'evidence'
    if payload.lesson_id:
        lesson = next(item for item in LESSONS if item['id'] == payload.lesson_id)
        if skill != lesson['skill']:
            raise HTTPException(422, 'The lesson requires its specified research workflow')
    blocked = []
    warnings = [LIMITS]
    if payload.language != 'en':
        blocked.append('The available encoder uses English keywords. Supply an explicitly translated English source before execution; no translation or scoring substitution is automatic.')
    if payload.consent == 'unconfirmed':
        warnings.append('Source permission is unconfirmed. Confirm research use before retaining or sharing this evidence.')
    if payload.model == 'agent_based' and skill != 'evidence':
        blocked.append('The existing agent-based proxy does not use intervention_strength. Select compartmental or hybrid for an intervention comparison; the harness will not substitute a model.')
    if payload.model == 'hybrid':
        warnings.append('Hybrid adoption blends 55% compartmental and 45% deterministic proxy output. Its reported compartments describe only the compartmental component.')
    if profile == 'thorough' and measured['recommended_profile'] == 'economy':
        warnings.append('Thorough was explicitly selected on a constrained host; execution stays serial within this experiment.')
    prior = []
    for run_id in dict.fromkeys(payload.prior_run_ids):
        previous = store.load(payload.workspace_id, run_id)
        if previous['status'] != 'completed' or not previous.get('review'):
            raise HTTPException(422, 'Prior context must be a completed run with an explicit researcher review')
        prior.append({'run_id': run_id, 'question': previous['title'], 'researcher_note': previous['review']['note'],
                      'reviewed_at': previous['review']['at'], 'use': 'Context only; does not alter model parameters.'})
    plan = [{'id': 'encode', 'tool': 'encode', 'title': 'Encode narrative signals', 'reason': 'English keyword interpretation of the supplied evidence.'},
            {'id': 'diagnose', 'tool': 'diagnose', 'title': 'Inspect inoculation signals', 'reason': 'Identify heuristic risks and retain the need for human review.'}]
    if skill != 'evidence':
        plan += [{'id': 'baseline', 'tool': 'simulate', 'title': 'Simulate the baseline', 'strength': 0.0, 'reason': 'Zero intervention; all remaining inputs match the alternative.'},
                 {'id': 'intervention', 'tool': 'simulate', 'title': 'Simulate the intervention', 'strength': payload.intervention_strength, 'reason': 'Change only the explicitly selected intervention strength.'}]
    grid = []
    if skill == 'sensitivity':
        count = measured['profiles'][profile]
        grid = [round(i / (count - 1), 6) for i in range(count)]
        for index, strength in enumerate(grid):
            plan.append({'id': f'sweep_{index}', 'tool': 'simulate', 'title': f'Sensitivity: strength {strength:g}', 'strength': strength,
                         'reason': 'One point in the disclosed deterministic grid; not a confidence interval.'})
    plan += [{'id': 'check', 'tool': 'check', 'title': 'Check numerical consistency', 'reason': 'Check finite values, bounds and normalized compartment totals where applicable.'},
             {'id': 'brief', 'tool': 'brief', 'title': 'Prepare the research artifacts', 'reason': 'Bundle the inputs, method, outputs and limitations.'}]
    context = {'country': ', '.join(workspace['settings'].get('countries', [])), 'domain': workspace['settings'].get('domain', ''),
               'language': payload.language, 'expertise': payload.expertise, 'source_name': payload.source_name, 'consent': payload.consent,
               'prior_reviewed_findings': prior, 'workspace_version': workspace.get('version'),
               'explanation': {'guided': 'Follow each step, inspect its assumptions, then review the draft before reuse.',
                               'researcher': 'Inspect method selection, parameter provenance and the numerical audit.',
                               'expert': 'Review complete tool outputs, normalized dynamics, environment and code fingerprint.'}[payload.expertise]}
    run_id = str(uuid4())
    return {'run_id': run_id, 'thread_id': payload.thread_id or run_id, 'workspace_id': payload.workspace_id, 'created_at': store.now(), 'updated_at': store.now(),
            'status': 'planned', 'title': payload.question, 'evidence': payload.evidence, 'skill': skill, 'lesson_id': payload.lesson_id,
            'request': payload.model_dump(), 'context': context, 'plan': plan, 'warnings': warnings, 'blockers': blocked,
            'execution': {'profile': profile, 'selection_reason': 'Measured CPU/memory envelope' if payload.profile == 'auto' else 'Explicit researcher selection',
                          'sensitivity_grid': grid, 'remote_calls': 0, 'provider_cost': 0,
                          'cost_note': 'No model-provider calls. Local compute cost is not estimated.', 'max_attempt_seconds': 30,
                          'method_substitution': False, 'resources': measured},
            'provenance': {'code_version': fingerprint(), 'environment': environment_manifest(),
                           'source_sha256': hashlib.sha256(payload.evidence.encode()).hexdigest(), 'planner': 'bounded_intent_rules_v1'},
            'outputs': {}, 'events': [], 'review': None, 'attempt': 0}


class Harness:
    def __init__(self):
        self.lock = threading.RLock()
        self.pool = None
        self.owner = None
        self.futures = {}
        self.stopping = False

    def start(self):
        with self.lock:
            if self.pool:
                return
            root = app_paths()['data']
            root.mkdir(parents=True, exist_ok=True)
            owner = sqlite3.connect(root / 'engine-owner.sqlite3', timeout=0, check_same_thread=False)
            try:
                owner.execute('BEGIN EXCLUSIVE')
            except sqlite3.OperationalError:
                owner.close()
                raise RuntimeError('The NIDM harness requires one server worker per data directory. Another owner is active.')
            self.owner = owner
            self.stopping = False
            self.recover()
            self.pool = ThreadPoolExecutor(max_workers=resources()['worker_limit'], thread_name_prefix='nidm-tool')

    def recover(self):
        for file in app_paths()['workspaces'].glob('*/evidence/engine-runs/*.json'):
            workspace = file.parents[2].name
            try:
                run = store.load(workspace, file.stem)
            except HTTPException:
                logger.warning('Unreadable experiment checkpoint: %s', file.name)
                continue
            if run['status'] in ACTIVE:
                run['status'] = 'interrupted'
                store.event(run, 'interrupted', 'The server stopped before completion. Review and resume from saved tool checkpoints.')
                store.save(run)

    def stop(self):
        with self.lock:
            self.stopping = True
            pool = self.pool
        if pool:
            pool.shutdown(wait=True)
        with self.lock:
            self.pool = None
            if self.owner:
                self.owner.rollback()
                self.owner.close()
                self.owner = None
            self.futures.clear()

    def submit(self, workspace, run_id, resume=False):
        with self.lock:
            if not self.pool or self.stopping:
                raise HTTPException(503, 'The execution worker is unavailable')
            run = store.load(workspace, run_id)
            allowed = {'failed', 'interrupted', 'cancelled'} if resume else {'planned'}
            if run['status'] not in allowed:
                raise HTTPException(409, 'This experiment is not eligible for this action')
            if run['blockers']:
                raise HTTPException(422, run['blockers'][0])
            if run['provenance']['code_version'] != fingerprint():
                raise HTTPException(409, 'Scientific code changed. Create a new plan; checkpoints cannot mix code versions.')
            if run['provenance']['environment'] != environment_manifest():
                raise HTTPException(409, 'The scientific environment changed. Create a new plan; checkpoints cannot mix environments.')
            self.futures = {key: future for key, future in self.futures.items() if not future.done()}
            if len(self.futures) >= 8:
                raise HTTPException(429, 'The local execution queue is full; retry after another experiment finishes')
            run['status'] = 'queued'
            run['attempt'] += 1
            store.event(run, 'approved', 'Researcher approved resuming the saved plan.' if resume else 'Researcher approved the plan and workspace persistence.')
            store.save(run)
            self.futures[(workspace, run_id)] = self.pool.submit(self.work, workspace, run_id)
            return public(run)

    def work(self, workspace, run_id):
        started = time.monotonic()
        try:
            while True:
                with self.lock:
                    run = store.load(workspace, run_id)
                    if run['status'] == 'cancelling' or self.stopping:
                        run['status'] = 'cancelled' if not self.stopping else 'interrupted'
                        store.event(run, run['status'], 'Stopped at a tool boundary. Completed checkpoints are retained.')
                        store.save(run)
                        return
                    pending = next((step for step in run['plan'] if step['id'] not in run['outputs']), None)
                    if pending is None:
                        run['status'] = 'completed'
                        store.event(run, 'completed', 'Experiment complete. Artifacts require researcher review.')
                        store.save(run)
                        return
                    if time.monotonic() - started > run['execution']['max_attempt_seconds']:
                        raise TimeoutError('Attempt budget exhausted')
                    run['status'] = 'running'
                    store.event(run, 'tool_started', pending['title'], tool_id=pending['id'])
                    store.save(run)
                result = execute_tool(pending, run)
                with self.lock:
                    latest = store.load(workspace, run_id)
                    if latest['status'] == 'cancelling' or self.stopping:
                        # Do not publish an in-flight output after cancellation wins.
                        continue
                    latest['outputs'][pending['id']] = result
                    store.event(latest, 'tool_completed', pending['title'], tool_id=pending['id'])
                    store.save(latest)
        except Exception as exc:
            logger.warning('Experiment %s stopped with %s', run_id, type(exc).__name__)
            with self.lock:
                try:
                    run = store.load(workspace, run_id)
                    run['status'] = 'cancelled' if run['status'] == 'cancelling' else 'failed'
                    store.event(run, run['status'], 'Execution stopped. Saved checkpoints are available for review and resume; internal error details are not exposed.')
                    store.save(run)
                except Exception:
                    # A storage outage leaves the last durable checkpoint for startup recovery.
                    pass


harness = Harness()


def reply(data, status_code=200):
    return JSONResponse(data, status_code=status_code, headers={'Cache-Control': 'no-store'})


@router.get('/capabilities')
def capabilities():
    return reply({'resources': resources(), 'planner': 'bounded intent rules; no general LLM reasoning',
                  'implemented': ['reviewable plans', 'domain tools', 'checkpoint resume', 'durable cancellation request', 'workspace artifacts', 'interactive lessons'],
                  'unavailable': ['LLM planner', 'sandboxed generated code', 'MCP', 'LLM subagents', 'user authentication'],
                  'access': 'Local shared instance; workspace IDs are not authorization boundaries.'})


@router.post('/plans', status_code=201)
def create_plan(payload: ExperimentRequest):
    run = build_plan(payload)
    store.event(run, 'planned', f"Prepared {run['skill']} workflow using bounded intent rules. Awaiting researcher approval.")
    with harness.lock:
        store.save(run)
    return reply(public(run), status_code=201)


@router.get('/workspaces/{workspace}/runs')
def history(workspace: str, offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100)):
    rows = store.listing(workspace)
    return reply({'runs': rows[offset:offset+limit], 'total': len(rows)})


@router.get('/workspaces/{workspace}/runs/{run_id}')
def get_run(workspace: str, run_id: str):
    return reply(public(store.load(workspace, run_id)))


@router.post('/workspaces/{workspace}/runs/{run_id}/start')
def start_run(workspace: str, run_id: str):
    return reply(harness.submit(workspace, run_id))


@router.post('/workspaces/{workspace}/runs/{run_id}/resume')
def resume_run(workspace: str, run_id: str):
    return reply(harness.submit(workspace, run_id, resume=True))


@router.post('/workspaces/{workspace}/runs/{run_id}/cancel')
def cancel_run(workspace: str, run_id: str):
    with harness.lock:
        run = store.load(workspace, run_id)
        if run['status'] not in ACTIVE | {'planned'}:
            raise HTTPException(409, 'Experiment has already stopped')
        run['status'] = 'cancelled' if run['status'] == 'planned' else 'cancelling'
        store.event(run, 'cancel_requested', 'Researcher requested cancellation. In-flight tools finish before the worker stops.')
        store.save(run)
    return reply(public(run))


@router.delete('/workspaces/{workspace}/runs/{run_id}', status_code=204)
def delete_run(workspace: str, run_id: str):
    with harness.lock:
        run = store.load(workspace, run_id)
        if run['status'] in ACTIVE:
            raise HTTPException(409, 'Cancel the active experiment before deleting it')
        store.path(workspace, run_id).unlink()
    return Response(status_code=204)


@router.post('/workspaces/{workspace}/runs/{run_id}/review')
def review_run(workspace: str, run_id: str, payload: ReviewRequest):
    with harness.lock:
        run = store.load(workspace, run_id)
        if run['status'] != 'completed':
            raise HTTPException(409, 'Complete the experiment before adding a review')
        run['review'] = {'note': payload.note.strip(), 'at': store.now(), 'status': 'researcher_reviewed_not_empirically_validated'}
        store.event(run, 'reviewed', 'Researcher saved a review note. This does not certify empirical validity.')
        store.save(run)
    return reply(public(run))


@router.get('/workspaces/{workspace}/runs/{run_id}/artifacts/{kind}')
def artifact(workspace: str, run_id: str, kind: Literal['json', 'brief']):
    run = store.load(workspace, run_id)
    if kind == 'brief' and run['status'] != 'completed':
        raise HTTPException(409, 'The brief is only available for a completed experiment')
    content = json.dumps(run, ensure_ascii=False, indent=2) if kind == 'json' else run['outputs']['brief']['markdown']
    return Response(content, media_type='application/json' if kind == 'json' else 'text/markdown',
                    headers={'Cache-Control': 'no-store', 'Content-Disposition': f'attachment; filename="nidm-{run_id}.{ "json" if kind == "json" else "md"}"'})


@router.get('/lessons')
def lessons():
    return reply({'lessons': public_lessons(), 'sample': SAMPLE})


@router.post('/workspaces/{workspace}/lessons/{lesson_id}/check')
def check_lesson(workspace: str, lesson_id: str, payload: LessonCheck):
    lesson = next((item for item in LESSONS if item['id'] == lesson_id), None)
    if not lesson:
        raise HTTPException(404, 'Lesson not found')
    with harness.lock:
        run = store.load(workspace, payload.run_id)
        if run['status'] != 'completed' or run['lesson_id'] != lesson_id:
            raise HTTPException(409, 'Complete this lesson experiment before checking your answer')
        correct = payload.choice == lesson['answer']
        run['lesson_check'] = {'correct': correct, 'choice': payload.choice, 'at': store.now(), 'explanation': lesson['explanation']}
        store.event(run, 'lesson_check', 'Learning check passed.' if correct else 'Learning check needs another attempt.')
        store.save(run)
    return reply(run['lesson_check'])
