"""Bounded research harness: explicit tools, streamed events, explicit workspace persistence.

The first skill deliberately uses deterministic domain tools. A future planner can
select these tools without owning their scientific implementation or permissions.
"""
import asyncio
import json
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse, Response
from pydantic import BaseModel, Field, field_validator

from .encoding import encode_rule_based
from .inoculation import diagnose_inoculation_rule_based
from .modelling import run_digital_twin, model_assumptions
from .schemas import NarrativeRecord, NarrativeMetadata, ModelMode
from .research_store import run_folder, save_run, load_run, list_runs, delete_run, code_version

router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    workspace_id: str | None = Field(default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=160)
    text: str = Field(min_length=20, max_length=20000)
    skill: Literal["evidence", "scenario"] = "evidence"
    horizon_days: int = Field(default=90, ge=7, le=365)
    intervention_strength: float = Field(default=0.3, ge=0, le=1)

    @field_validator("text")
    @classmethod
    def meaningful_text(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 20:
            raise ValueError("Provide at least 20 characters of narrative evidence.")
        return value


SKILLS = [
    {"id": "evidence", "name": "Understand a narrative", "tools": ["encode", "diagnose", "brief"]},
    {"id": "scenario", "name": "Explore a scenario", "tools": ["encode", "diagnose", "simulate", "brief"]},
]


@router.get("/capabilities")
def capabilities():
    return {"mode": "deterministic", "skills": SKILLS, "remote_calls": False,
            "memory": "optional_workspace", "workspace_access": "local_shared_instance",
            "retention": "until_explicit_deletion", "mcp": False, "sandbox": False, "subagents": False}


def execute_research(payload: ResearchRequest):
    """Yield only observed tool results; never invent planning or execution activity."""
    run_id = str(uuid4())
    steps = next(skill["tools"] for skill in SKILLS if skill["id"] == payload.skill)
    yield {"type": "plan", "run_id": run_id, "steps": steps, "mode": "deterministic"}
    record = NarrativeRecord(narrative_id=run_id, text=payload.text,
                             metadata=NarrativeMetadata(source_type="text", country="Rwanda"))
    yield {"type": "step", "tool": "encode", "status": "running"}
    encoded = encode_rule_based(record)
    yield {"type": "step", "tool": "encode", "status": "completed"}
    yield {"type": "step", "tool": "diagnose", "status": "running"}
    diagnosis = diagnose_inoculation_rule_based(record, encoded)
    yield {"type": "step", "tool": "diagnose", "status": "completed"}
    scenario = None
    if payload.skill == "scenario":
        yield {"type": "step", "tool": "simulate", "status": "running"}
        parameters = {"trust_score": encoded.trust_score, "barrier_score": encoded.adoption_barrier_score,
                      "confidence": encoded.confidence, "intervention_strength": 0.0,
                      "misinformation_risk": diagnosis.misinformation_risk_score}
        intervention = {**parameters, "intervention_strength": payload.intervention_strength}
        scenario = {"horizon_days": payload.horizon_days,
                    "baseline": run_digital_twin(ModelMode.compartmental, payload.horizon_days, parameters),
                    "intervention": run_digital_twin(ModelMode.compartmental, payload.horizon_days, intervention),
                    "baseline_assumptions": model_assumptions(ModelMode.compartmental, parameters),
                    "intervention_assumptions": model_assumptions(ModelMode.compartmental, intervention)}
        yield {"type": "step", "tool": "simulate", "status": "completed"}
    yield {"type": "step", "tool": "brief", "status": "running"}
    caveat = ("Exploratory draft requiring human review. Scores are English keyword heuristics, not validated "
              "measurements or findings of fact. One narrative cannot establish population prevalence, "
              "causality, or whether a claim is false. Scenarios are illustrative, not forecasts; their "
              "bands are heuristic, not statistical confidence intervals.")
    brief = (f"# Narrative evidence brief\n\nRun: {run_id}\n\n"
             f"## Source\n\n{payload.text}\n\n"
             f"## Heuristic signals\n\nThemes: {', '.join(encoded.themes)}\n\n"
             f"Trust: {encoded.trust_score:.2f} / 1\n\nAdoption barrier: {encoded.adoption_barrier_score:.2f} / 1\n\n"
             f"## Review next\n\nCheck the original source, consent, context and language. "
             f"Verify the keyword-derived themes with a researcher before using them in the evidence ledger.\n\n"
             f"## Limits\n\n{caveat}\n")
    if scenario:
        brief += (f"\n## Illustrative scenario\n\nHorizon: {payload.horizon_days} days. "
                  f"Baseline intervention strength: 0. Intervention strength: {payload.intervention_strength}. "
                  f"Final model adoption: {scenario['baseline'][-1]['adoption']:.3f} baseline; "
                  f"{scenario['intervention'][-1]['adoption']:.3f} intervention. "
                  "See the JSON artifact for complete parameters and trajectories.\n")
    result = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(),
              "skill": payload.skill, "mode": "deterministic", "source": record.model_dump(mode="json"),
              "encoding": encoded.model_dump(mode="json"), "diagnosis": diagnosis.model_dump(mode="json"),
              "scenario": scenario, "brief": brief, "caveat": caveat, "review_status": "requires_review"}
    yield {"type": "step", "tool": "brief", "status": "completed"}
    yield {"type": "result", "result": result}


@router.post("/runs")
async def run_research(payload: ResearchRequest, request: Request):
    if payload.workspace_id:
        run_folder(payload.workspace_id)  # Validate before opening the response stream.
    version = code_version()
    async def stream():
        events = []
        try:
            for event in execute_research(payload):
                if await request.is_disconnected():
                    return
                if event["type"] == "result":
                    event["result"].update({"workspace_id": payload.workspace_id,
                                            "code_version": version,
                                            "request": payload.model_dump(mode="json"),
                                            "events": events,
                                            "status": "completed"})
                    if payload.workspace_id:
                        save_run(payload.workspace_id, event["result"])
                else:
                    events.append({**event, "observed_at": datetime.now(timezone.utc).isoformat()})
                yield json.dumps(event, ensure_ascii=False) + "\n"
                await asyncio.sleep(0)  # Let disconnects interrupt between bounded tools.
        except Exception:
            yield json.dumps({"type": "error", "message": "Research could not complete or save its results. Retry or use the research workbench."}) + "\n"
    return StreamingResponse(stream(), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})


@router.get("/workspaces/{workspace_id}/runs")
def history(workspace_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    rows = list_runs(workspace_id)
    return JSONResponse({"runs": rows[offset:offset + limit], "total": len(rows)},
                        headers={"Cache-Control": "no-store"})


@router.get("/workspaces/{workspace_id}/runs/{run_id}")
def saved_run(workspace_id: str, run_id: str):
    return JSONResponse(load_run(workspace_id, run_id), headers={"Cache-Control": "no-store"})


@router.get("/workspaces/{workspace_id}/runs/{run_id}/artifacts/{kind}")
def artifact(workspace_id: str, run_id: str, kind: Literal["brief", "json"]):
    result = load_run(workspace_id, run_id)
    return Response(result["brief"] if kind == "brief" else json.dumps(result, ensure_ascii=False),
                    media_type="text/markdown" if kind == "brief" else "application/json",
                    headers={"Cache-Control": "no-store",
                             "Content-Disposition": f'attachment; filename="nidm-{run_id}.{"md" if kind == "brief" else "json"}"'})


@router.delete("/workspaces/{workspace_id}/runs/{run_id}", status_code=204)
def remove_run(workspace_id: str, run_id: str):
    delete_run(workspace_id, run_id)
    return Response(status_code=204)
