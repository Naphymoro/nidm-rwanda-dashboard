from __future__ import annotations

from statistics import mean
from typing import Any, Dict, Iterable, List


VALIDATION_DATASET: List[Dict[str, Any]] = [
    {
        "narrative_id": "val-rw-001",
        "route": "structured_interview",
        "region": "Rwanda / Southern Province / Nyamagabe",
        "text": "The respondent trusts the health worker demonstration and wants less smoke, but the purchase price and repair distance worry the household.",
        "expected_themes": ["affordability", "health", "trust", "maintenance"],
        "coder_a": {"trust": 0.72, "barrier": 0.58, "confidence": 0.82},
        "coder_b": {"trust": 0.68, "barrier": 0.62, "confidence": 0.78},
    },
    {
        "narrative_id": "val-rw-002",
        "route": "open_story",
        "region": "Rwanda / Northern Province / Musanze",
        "text": "Neighbours repeated a rumour that pressure cookers explode, but a women's group corrected it after a safe demonstration.",
        "expected_themes": ["safety", "misinformation", "social_influence", "trust"],
        "coder_a": {"trust": 0.60, "barrier": 0.52, "confidence": 0.76},
        "coder_b": {"trust": 0.63, "barrier": 0.49, "confidence": 0.74},
    },
    {
        "narrative_id": "val-rw-003",
        "route": "indigenous_knowledge",
        "region": "Rwanda / Western Province / Rubavu",
        "text": "An elder said seasonal firewood scarcity changes cooking choices, and any new device should respect shared cooking practices.",
        "expected_themes": ["fuel_access", "social_norms", "indigenous_knowledge"],
        "coder_a": {"trust": 0.56, "barrier": 0.47, "confidence": 0.70},
        "coder_b": {"trust": 0.54, "barrier": 0.50, "confidence": 0.72},
    },
    {
        "narrative_id": "val-rw-004",
        "route": "citizen_science",
        "region": "Rwanda / Eastern Province / Kayonza",
        "text": "A contributor observed less smoke in a neighbour's kitchen after switching, but could not verify fuel cost changes.",
        "expected_themes": ["health", "fuel_access", "uncertainty"],
        "coder_a": {"trust": 0.58, "barrier": 0.38, "confidence": 0.58},
        "coder_b": {"trust": 0.55, "barrier": 0.41, "confidence": 0.55},
    },
    {
        "narrative_id": "val-rw-005",
        "route": "social_feed",
        "region": "Rwanda / Kigali City / Gasabo",
        "text": "A Facebook post claims only rich families can use clean cooking, while comments mention subsidies and peer demonstrations.",
        "expected_themes": ["affordability", "misinformation", "policy_support", "social_influence"],
        "coder_a": {"trust": 0.46, "barrier": 0.66, "confidence": 0.64},
        "coder_b": {"trust": 0.44, "barrier": 0.69, "confidence": 0.62},
    },
]


def _score(record: Dict[str, Any], key: str) -> float:
    return float(record.get(key, 0.0) or 0.0)


def _human_average(row: Dict[str, Any], key: str) -> float:
    return mean([_score(row["coder_a"], key), _score(row["coder_b"], key)])


def _within_range(value: float, target: float, tolerance: float = 0.18) -> bool:
    return abs(value - target) <= tolerance


def _theme_metrics(expected: Iterable[str], predicted: Iterable[str]) -> Dict[str, float]:
    exp = set(expected)
    pred = set(predicted)
    tp = len(exp & pred)
    fp = len(pred - exp)
    fn = len(exp - pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"theme_precision": precision, "theme_recall": recall, "theme_f1": f1}


def inter_rater_reliability(dataset: List[Dict[str, Any]] | None = None) -> Dict[str, float]:
    rows = dataset or VALIDATION_DATASET
    if not rows:
        return {"trust_agreement": 0.0, "barrier_agreement": 0.0, "confidence_agreement": 0.0, "mean_agreement": 0.0}
    agreements: Dict[str, List[float]] = {"trust": [], "barrier": [], "confidence": []}
    for row in rows:
        for key in agreements:
            agreements[key].append(max(0.0, 1.0 - abs(_score(row["coder_a"], key) - _score(row["coder_b"], key))))
    trust = mean(agreements["trust"])
    barrier = mean(agreements["barrier"])
    confidence = mean(agreements["confidence"])
    return {
        "trust_agreement": trust,
        "barrier_agreement": barrier,
        "confidence_agreement": confidence,
        "mean_agreement": mean([trust, barrier, confidence]),
    }


def evaluate_encoder_against_validation(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_id = {item.get("narrative_id"): item for item in predictions}
    matched = [row for row in VALIDATION_DATASET if row["narrative_id"] in by_id]
    if not matched:
        return {
            "matched_records": 0,
            "status": "not_evaluated",
            "calibrated_for_policy": False,
            "warning": "No validation records were encoded in this run.",
            **inter_rater_reliability(),
        }

    trust_errors: List[float] = []
    barrier_errors: List[float] = []
    confidence_errors: List[float] = []
    theme_scores: List[Dict[str, float]] = []
    outside_range: List[str] = []
    for row in matched:
        pred = by_id[row["narrative_id"]]
        trust_target = _human_average(row, "trust")
        barrier_target = _human_average(row, "barrier")
        confidence_target = _human_average(row, "confidence")
        trust_value = float(pred.get("trust_score", 0.5) or 0.5)
        barrier_value = float(pred.get("adoption_barrier_score", 0.5) or 0.5)
        confidence_value = float(pred.get("confidence", 0.5) or 0.5)
        trust_errors.append(abs(trust_value - trust_target))
        barrier_errors.append(abs(barrier_value - barrier_target))
        confidence_errors.append(abs(confidence_value - confidence_target))
        theme_scores.append(_theme_metrics(row["expected_themes"], pred.get("themes", [])))
        if not _within_range(trust_value, trust_target):
            outside_range.append(f"{row['narrative_id']} trust")
        if not _within_range(barrier_value, barrier_target):
            outside_range.append(f"{row['narrative_id']} barrier")

    theme_precision = mean([score["theme_precision"] for score in theme_scores])
    theme_recall = mean([score["theme_recall"] for score in theme_scores])
    theme_f1 = mean([score["theme_f1"] for score in theme_scores])
    trust_mae = mean(trust_errors)
    barrier_mae = mean(barrier_errors)
    confidence_mae = mean(confidence_errors)
    agreement = inter_rater_reliability()
    calibrated = theme_f1 >= 0.55 and trust_mae <= 0.18 and barrier_mae <= 0.18 and agreement["mean_agreement"] >= 0.80
    return {
        "matched_records": len(matched),
        "status": "calibrated" if calibrated else "needs_review",
        "calibrated_for_policy": calibrated,
        "theme_precision": theme_precision,
        "theme_recall": theme_recall,
        "theme_f1": theme_f1,
        "trust_mae": trust_mae,
        "barrier_mae": barrier_mae,
        "confidence_mae": confidence_mae,
        "outside_expected_ranges": outside_range,
        **agreement,
        "warning": "" if calibrated else "Encoder agreement is not strong enough for policy use without human review.",
    }


def validation_status() -> Dict[str, Any]:
    agreement = inter_rater_reliability()
    return {
        "dataset_records": len(VALIDATION_DATASET),
        "double_coded": True,
        "agreement": agreement,
        "policy_thresholds": {
            "theme_f1_min": 0.55,
            "trust_mae_max": 0.18,
            "barrier_mae_max": 0.18,
            "inter_rater_mean_min": 0.80,
        },
        "note": "Validation dataset is intentionally small and should be expanded with real double-coded field narratives before high-stakes use.",
    }
