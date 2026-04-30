from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import math


class ThemeLabel(BaseModel):
    narrative_id: str
    themes: List[str] = Field(default_factory=list)
    adoption_barrier_score: Optional[float] = None
    trust_score: Optional[float] = None


class EncodingEvaluationRequest(BaseModel):
    ground_truth: List[ThemeLabel]
    predictions: List[ThemeLabel]


class SimulationPoint(BaseModel):
    day: int
    observed: float
    predicted: float


class SimulationEvaluationRequest(BaseModel):
    points: List[SimulationPoint]


def _safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def evaluate_encoding(req: EncodingEvaluationRequest) -> Dict[str, float]:
    truth = {x.narrative_id: x for x in req.ground_truth}
    preds = {x.narrative_id: x for x in req.predictions}
    ids = sorted(set(truth).intersection(preds))

    tp = fp = fn = 0
    barrier_errors = []
    trust_errors = []

    for nid in ids:
        t_themes = set(truth[nid].themes)
        p_themes = set(preds[nid].themes)
        tp += len(t_themes.intersection(p_themes))
        fp += len(p_themes - t_themes)
        fn += len(t_themes - p_themes)

        if truth[nid].adoption_barrier_score is not None and preds[nid].adoption_barrier_score is not None:
            barrier_errors.append(abs(truth[nid].adoption_barrier_score - preds[nid].adoption_barrier_score))
        if truth[nid].trust_score is not None and preds[nid].trust_score is not None:
            trust_errors.append(abs(truth[nid].trust_score - preds[nid].trust_score))

    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall)

    return {
        "matched_records": float(len(ids)),
        "theme_precision": precision,
        "theme_recall": recall,
        "theme_f1": f1,
        "barrier_mae": sum(barrier_errors) / len(barrier_errors) if barrier_errors else 0.0,
        "trust_mae": sum(trust_errors) / len(trust_errors) if trust_errors else 0.0,
    }


def evaluate_simulation(req: SimulationEvaluationRequest) -> Dict[str, float]:
    if not req.points:
        return {"n_points": 0.0, "mae": 0.0, "rmse": 0.0}

    errors = [p.predicted - p.observed for p in req.points]
    abs_errors = [abs(e) for e in errors]
    sq_errors = [e * e for e in errors]

    return {
        "n_points": float(len(req.points)),
        "mae": sum(abs_errors) / len(abs_errors),
        "rmse": math.sqrt(sum(sq_errors) / len(sq_errors)),
    }
