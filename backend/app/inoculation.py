import json
import re
import urllib.error
from typing import Any, Dict, List, Optional

from .encoding import (
    PROVIDER_DEFAULTS,
    OpenAI,
    _default_base_url,
    _extract_json,
    _post_json,
    _provider_key,
    llm_provider_status,
    normalize_provider,
)
from .llm_prompts import INOCULATION_DIAGNOSIS_SYSTEM_PROMPT, INOCULATION_DIAGNOSIS_USER_TEMPLATE
from .schemas import EncodedNarrative, InoculationEncoding, NarrativeRecord


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _hits(text: str, words: List[str]) -> int:
    return sum(len(re.findall(rf"\b{re.escape(word)}\b", text)) for word in words)


def _first_span(text: str, words: List[str], radius: int = 52) -> Optional[str]:
    lower = text.lower()
    for word in words:
        match = re.search(rf"\b{re.escape(word.lower())}\b", lower)
        if match:
            start = max(0, match.start() - radius)
            end = min(len(text), match.end() + radius)
            return text[start:end].strip()
    return None


def _pick_source_actor(text: str) -> str:
    actors = [
        (["health worker", "nurse", "clinic"], "health worker"),
        (["leader", "village leader", "sector leader", "church"], "local leader"),
        (["elder", "grandmother", "grandfather", "mother"], "elder or family authority"),
        (["neighbor", "neighbour", "friend", "peer"], "peer household"),
        (["vendor", "seller", "technician", "repair"], "vendor or technician"),
        (["radio", "whatsapp", "facebook", "twitter", "x ", "youtube", "tiktok"], "media or social feed"),
        (["government", "official", "policy"], "government or programme actor"),
    ]
    lower = text.lower()
    for words, label in actors:
        if any(word in lower for word in words):
            return label
    return "community conversation"


def _pick_group(text: str) -> str:
    groups = [
        (["women", "mother", "children", "child", "care"], "women caregivers and households with children"),
        (["farmer", "rural", "village"], "rural households"),
        (["low income", "poor", "money", "cost", "expensive"], "cost-sensitive households"),
        (["youth", "young"], "young adults"),
        (["elder", "traditional", "culture"], "elders and culturally grounded households"),
    ]
    lower = text.lower()
    for words, label in groups:
        if any(word in lower for word in words):
            return label
    return "households considering clean cooking"


def _pick_threat_type(text: str, counts: Dict[str, int]) -> str:
    if counts["safety"] and counts["misinformation"]:
        return "safety_misinformation"
    if counts["cost"]:
        return "affordability_fear"
    if counts["fuel"]:
        return "fuel_access_claim"
    if counts["distrust"]:
        return "institutional_distrust"
    if counts["culture"]:
        return "cultural_identity_threat"
    if counts["social"]:
        return "social_norm_pressure"
    if counts["maintenance"]:
        return "maintenance_or_supply_doubt"
    return "none_detected"


def _pick_mechanism(text: str, counts: Dict[str, int]) -> str:
    lower = text.lower()
    if any(word in lower for word in ["rumor", "rumour", "they say", "people say", "heard"]):
        return "rumor"
    if counts["safety"] and any(word in lower for word in ["explode", "burn", "poison", "danger"]):
        return "fear_appeal"
    if any(word in lower for word in ["always", "never", "everyone", "nobody"]):
        return "anecdotal_overgeneralization"
    if any(word in lower for word in ["government", "official", "programme", "program"]):
        return "authority_confusion"
    if any(word in lower for word in ["status", "rich", "modern", "poor"]):
        return "status_stigma"
    if counts["fuel"]:
        return "false_scarcity"
    if counts["maintenance"]:
        return "technical_misunderstanding"
    return "none_detected"


def _make_counter_text(threat_type: str, messenger: str) -> Dict[str, str]:
    weak = {
        "safety_misinformation": "Some people may hear that pressure cookers or clean-cooking devices are automatically unsafe.",
        "affordability_fear": "Some people may hear that clean cooking is only for wealthy households.",
        "fuel_access_claim": "Some people may hear that the needed fuel or repair support will not be available locally.",
        "institutional_distrust": "Some people may hear that the programme is only another outside promise.",
        "cultural_identity_threat": "Some people may hear that clean cooking means rejecting respected local cooking knowledge.",
        "social_norm_pressure": "Some people may hear that neighbours will judge or reject families who change cooking practice.",
        "maintenance_or_supply_doubt": "Some people may hear that the device will break and no one will help.",
        "none_detected": "Some people may still have questions before they trust a new cooking practice.",
    }.get(threat_type, "Some people may hear a misleading claim about clean cooking.")
    refute = {
        "safety_misinformation": "Safety should be judged through supervised demonstrations, correct use, maintenance support, and reports from local users, not through a rumour alone.",
        "affordability_fear": "Cost concerns are real, but they should be compared with fuel savings, time savings, financing options, and maintenance access.",
        "fuel_access_claim": "Fuel and repair claims should be checked against local supply points, trained technicians, and actual household experience.",
        "institutional_distrust": "Trust improves when local reviewers, transparent costs, and community-selected messengers verify the programme.",
        "cultural_identity_threat": "Clean cooking should be presented as protecting health and time while respecting local food practices and community knowledge.",
        "social_norm_pressure": "Peer demonstrations can make adoption visible and ordinary rather than risky or shameful.",
        "maintenance_or_supply_doubt": "A credible intervention should include repair guidance, warranty clarity, and a named support contact.",
        "none_detected": "Questions should be answered with local demonstrations, transparent evidence, and room for human review.",
    }.get(threat_type, "The claim should be checked with local evidence and trusted demonstration.")
    return {
        "weak_dose_claim": weak,
        "refutational_preemption": refute,
        "counter_narrative": f"Before deciding from a claim alone, ask {messenger} to compare the rumour with local demonstration evidence, household costs, safety practice, and repair support.",
        "booster_strategy": f"Repeat the correction through {messenger}, a peer demonstration, and a follow-up household check after first use.",
    }


def diagnose_inoculation_rule_based(
    record: NarrativeRecord,
    encoded: Optional[EncodedNarrative] = None,
    note: str = "deterministic inoculation heuristic fallback",
) -> InoculationEncoding:
    text = record.text or ""
    lower = text.lower()
    provenance = record.metadata.provenance or {}
    route = str(provenance.get("evidence_mode") or record.metadata.source_type or "").lower()
    counts = {
        "misinformation": _hits(lower, ["rumor", "rumour", "false", "fake", "misleading", "claim", "heard", "myth", "witchcraft"]),
        "safety": _hits(lower, ["unsafe", "safe", "explode", "explosion", "burn", "pressure", "danger", "poison"]),
        "cost": _hits(lower, ["cost", "expensive", "price", "money", "loan", "subsidy", "afford", "saving", "payment"]),
        "fuel": _hits(lower, ["fuel", "charcoal", "firewood", "lpg", "electricity", "pellet", "supply"]),
        "distrust": _hits(lower, ["distrust", "doubt", "cheated", "broken", "failed", "promise", "government", "programme", "program"]),
        "culture": _hits(lower, ["tradition", "traditional", "culture", "elder", "taste", "custom", "indigenous", "ancestral"]),
        "social": _hits(lower, ["people", "neighbour", "neighbor", "family", "women", "group", "church", "cooperative", "peer", "meeting"]),
        "maintenance": _hits(lower, ["repair", "maintenance", "spare", "warranty", "technician", "broken"]),
        "positive": _hits(lower, ["trusted", "demonstration", "showed", "trained", "saved", "less smoke", "faster", "benefit"]),
        "emotion": _hits(lower, ["fear", "afraid", "worried", "angry", "ashamed", "hope", "relieved", "proud", "stress"]),
        "local": _hits(lower, ["district", "sector", "village", "cell", "market", "community", "province"]),
    }
    if record.metadata.country:
        counts["local"] += 1
    if record.metadata.admin_unit:
        counts["local"] += 1
    if "indigenous" in route:
        counts["culture"] += 2

    threat_type = _pick_threat_type(lower, counts)
    mechanism = _pick_mechanism(lower, counts)
    messenger = _pick_source_actor(lower)
    susceptible = _pick_group(lower)
    trigger = (
        "fear and safety anxiety" if counts["safety"] or counts["emotion"]
        else "cost anxiety" if counts["cost"]
        else "identity and tradition" if counts["culture"]
        else "social proof and peer pressure" if counts["social"]
        else "uncertainty"
    )

    trust = encoded.trust_score if encoded and encoded.trust_score is not None else 0.55
    barrier = encoded.adoption_barrier_score if encoded and encoded.adoption_barrier_score is not None else 0.40
    encoded_conf = encoded.confidence if encoded and encoded.confidence is not None else 0.45

    threat_score = _clamp(0.18 + 0.10 * counts["misinformation"] + 0.08 * counts["safety"] + 0.05 * counts["emotion"] + 0.05 * barrier)
    misinformation_score = _clamp(0.12 + 0.13 * counts["misinformation"] + 0.08 * counts["safety"] + 0.05 * counts["distrust"])
    identity_score = _clamp(0.08 + 0.11 * counts["culture"] + 0.04 * counts["social"])
    reactance_score = _clamp(0.10 + 0.09 * counts["distrust"] + 0.04 * counts["culture"] + 0.04 * (1 - trust))
    cultural_score = _clamp(0.10 + 0.13 * counts["culture"] + (0.10 if "indigenous" in route else 0.0))
    refutability = _clamp(0.22 + 0.07 * counts["local"] + 0.07 * counts["positive"] + 0.04 * trust - 0.03 * reactance_score)
    messenger_fit = _clamp(0.28 + 0.08 * counts["local"] + 0.08 * counts["positive"] + 0.06 * trust)
    resilience = _clamp(0.24 + 0.20 * trust + 0.18 * refutability + 0.12 * messenger_fit - 0.12 * misinformation_score)
    confidence = _clamp(0.30 + 0.10 * encoded_conf + 0.05 * counts["local"] + min(len(text.split()), 160) / 900)
    booster_needed = misinformation_score >= 0.45 or reactance_score >= 0.48 or cultural_score >= 0.55
    counter = _make_counter_text(threat_type, messenger)
    inoculation_strength = _clamp(
        0.10
        + threat_score * 0.20
        + misinformation_score * 0.20
        + refutability * 0.18
        + messenger_fit * 0.14
        - reactance_score * 0.08
    )

    return InoculationEncoding(
        narrative_id=record.narrative_id,
        diagnosis_mode="heuristic",
        narrative_type="misinformation_risk" if threat_type != "none_detected" else "adoption_context",
        threat_type=threat_type,
        misinformation_mechanism=mechanism,
        source_actor=messenger,
        susceptible_group=susceptible,
        psychological_trigger=trigger,
        threat_recognition_score=round(threat_score, 3),
        misinformation_risk_score=round(misinformation_score, 3),
        identity_threat_score=round(identity_score, 3),
        reactance_risk_score=round(reactance_score, 3),
        cultural_sensitivity_score=round(cultural_score, 3),
        refutability_score=round(refutability, 3),
        trusted_messenger=messenger,
        trusted_messenger_fit_score=round(messenger_fit, 3),
        weak_dose_claim=counter["weak_dose_claim"],
        refutational_preemption=counter["refutational_preemption"],
        counter_narrative=counter["counter_narrative"],
        booster_strategy=counter["booster_strategy"],
        booster_needed=booster_needed,
        narrative_resilience_score=round(resilience, 3),
        confidence=round(confidence, 3),
        evidence_spans={
            "threat": _first_span(text, ["rumor", "rumour", "false", "unsafe", "explode", "expensive", "fuel", "government"]),
            "source": _first_span(text, ["health worker", "leader", "elder", "neighbor", "neighbour", "radio", "whatsapp", "vendor"]),
            "trigger": _first_span(text, ["fear", "afraid", "cost", "expensive", "tradition", "people", "family", "repair"]),
            "messenger": _first_span(text, ["trusted", "demonstration", "showed", "trained", "health worker", "leader", "neighbour", "neighbor"]),
            "uncertainty": None if confidence > 0.55 else "Narrative is short, ambiguous, or weakly grounded.",
        },
        intervention_parameters={
            "inoculation_strength": round(inoculation_strength, 3),
            "misinformation_decay": round(_clamp(0.04 + refutability * 0.22 + messenger_fit * 0.12), 3),
            "resistance_growth": round(_clamp(0.04 + resilience * 0.24 + messenger_fit * 0.10), 3),
            "trust_shift": round(_clamp(0.01 + messenger_fit * 0.09 + refutability * 0.05), 3),
            "barrier_shift": round(-_clamp(0.01 + refutability * 0.06 + misinformation_score * 0.03), 3),
            "reactance_penalty": round(_clamp(reactance_score * (0.45 + cultural_score * 0.35)), 3),
            "trusted_messenger_fit": round(messenger_fit, 3),
            "misinformation_risk": round(misinformation_score, 3),
        },
        model_notes=f"{note}; threat={threat_type}; mechanism={mechanism}; human review required before field use.",
    )


def _diagnosis_from_data(
    record: NarrativeRecord,
    data: Dict[str, Any],
    note: str,
    mode: str = "llm",
) -> InoculationEncoding:
    fallback = diagnose_inoculation_rule_based(record, note=f"{note}; schema fallback for missing fields")
    base = fallback.model_dump()
    base.update({key: value for key, value in data.items() if value not in (None, "")})
    intervention = {**fallback.intervention_parameters, **(data.get("intervention_parameters") or {})}
    base["intervention_parameters"] = {key: round(_clamp(float(value), -1.0, 1.0), 3) for key, value in intervention.items()}
    for key in [
        "threat_recognition_score",
        "misinformation_risk_score",
        "identity_threat_score",
        "reactance_risk_score",
        "cultural_sensitivity_score",
        "refutability_score",
        "trusted_messenger_fit_score",
        "narrative_resilience_score",
        "confidence",
    ]:
        base[key] = round(_clamp(float(base.get(key, 0.0))), 3)
    base["narrative_id"] = record.narrative_id
    base["diagnosis_mode"] = mode
    base["human_review_status"] = "requires_review"
    base["model_notes"] = note
    return InoculationEncoding(**base)


def _messages(record: NarrativeRecord, encoded: Optional[EncodedNarrative]) -> List[Dict[str, str]]:
    encoding_payload = json.dumps(encoded.model_dump() if encoded else {}, ensure_ascii=False)
    return [
        {"role": "system", "content": INOCULATION_DIAGNOSIS_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": INOCULATION_DIAGNOSIS_USER_TEMPLATE.format(text=record.text, encoding=encoding_payload),
        },
    ]


def _diagnose_openai_compatible(
    record: NarrativeRecord,
    encoded: Optional[EncodedNarrative],
    provider: str,
    api_key: Optional[str],
    base_url: Optional[str],
    model: Optional[str],
) -> InoculationEncoding:
    if not OpenAI:
        return diagnose_inoculation_rule_based(record, encoded, f"{provider} SDK unavailable; deterministic inoculation fallback")
    status = llm_provider_status(provider, api_key, base_url, model)
    key = _provider_key(status["provider"], api_key)
    if not key and status["provider"] not in {"lmstudio", "openai-compatible"}:
        return diagnose_inoculation_rule_based(record, encoded, f"{status['provider']} key missing; deterministic inoculation fallback")
    kwargs: Dict[str, Any] = {"api_key": key or "local"}
    endpoint = base_url or _default_base_url(status["provider"])
    if endpoint:
        kwargs["base_url"] = endpoint
    client = OpenAI(**kwargs)
    response = client.chat.completions.create(
        model=status["model"],
        messages=_messages(record, encoded),
        temperature=0.15,
    )
    data = _extract_json(response.choices[0].message.content or "{}")
    return _diagnosis_from_data(record, data, f"{status['provider']} inoculation diagnosis; credential_source={status['credential_source']}")


def _diagnose_anthropic(record: NarrativeRecord, encoded: Optional[EncodedNarrative], api_key: Optional[str], model: Optional[str]) -> InoculationEncoding:
    key = _provider_key("anthropic", api_key)
    if not key:
        return diagnose_inoculation_rule_based(record, encoded, "anthropic key missing; deterministic inoculation fallback")
    body = {
        "model": model or PROVIDER_DEFAULTS["anthropic"]["model"],
        "max_tokens": 1300,
        "temperature": 0.15,
        "system": INOCULATION_DIAGNOSIS_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": INOCULATION_DIAGNOSIS_USER_TEMPLATE.format(text=record.text, encoding=json.dumps(encoded.model_dump() if encoded else {}))}],
    }
    result = _post_json(PROVIDER_DEFAULTS["anthropic"]["base_url"] or "", body, {"x-api-key": key, "anthropic-version": "2023-06-01"})
    content = "".join(part.get("text", "") for part in result.get("content", []) if isinstance(part, dict))
    return _diagnosis_from_data(record, _extract_json(content), "anthropic inoculation diagnosis")


def _diagnose_gemini(
    record: NarrativeRecord,
    encoded: Optional[EncodedNarrative],
    api_key: Optional[str],
    model: Optional[str],
    base_url: Optional[str],
) -> InoculationEncoding:
    key = _provider_key("gemini", api_key)
    if not key:
        return diagnose_inoculation_rule_based(record, encoded, "gemini key missing; deterministic inoculation fallback")
    model_name = model or PROVIDER_DEFAULTS["gemini"]["model"]
    root = (base_url or PROVIDER_DEFAULTS["gemini"]["base_url"] or "").rstrip("/")
    url = f"{root}/models/{model_name}:generateContent?key={key}"
    body = {
        "contents": [{"role": "user", "parts": [{"text": f"{INOCULATION_DIAGNOSIS_SYSTEM_PROMPT}\n\n{INOCULATION_DIAGNOSIS_USER_TEMPLATE.format(text=record.text, encoding=json.dumps(encoded.model_dump() if encoded else {}))}"}]}],
        "generationConfig": {"temperature": 0.15},
    }
    result = _post_json(url, body, {})
    text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return _diagnosis_from_data(record, _extract_json(text), "gemini inoculation diagnosis")


def _diagnose_ollama(
    record: NarrativeRecord,
    encoded: Optional[EncodedNarrative],
    provider: str,
    base_url: Optional[str],
    model: Optional[str],
) -> InoculationEncoding:
    endpoint = base_url or _default_base_url(provider) or PROVIDER_DEFAULTS["ollama"]["base_url"]
    body = {
        "model": model or PROVIDER_DEFAULTS[provider]["model"],
        "messages": _messages(record, encoded),
        "stream": False,
        "options": {"temperature": 0.15},
    }
    result = _post_json(endpoint or "", body, {})
    return _diagnosis_from_data(record, _extract_json(result.get("message", {}).get("content", "")), f"{provider} local inoculation diagnosis")


def diagnose_inoculation(
    record: NarrativeRecord,
    encoded: Optional[EncodedNarrative] = None,
    provider: Optional[str] = "openai",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> InoculationEncoding:
    normalized = normalize_provider(provider)
    if normalized == "deterministic":
        return diagnose_inoculation_rule_based(record, encoded, "deterministic inoculation fallback selected")
    try:
        if normalized == "anthropic":
            return _diagnose_anthropic(record, encoded, api_key, model)
        if normalized == "gemini":
            return _diagnose_gemini(record, encoded, api_key, model, base_url)
        if normalized in {"ollama", "local"}:
            return _diagnose_ollama(record, encoded, normalized, base_url, model)
        return _diagnose_openai_compatible(record, encoded, normalized, api_key, base_url, model)
    except (json.JSONDecodeError, urllib.error.URLError, TimeoutError, Exception) as exc:
        return diagnose_inoculation_rule_based(record, encoded, f"{normalized} inoculation diagnosis failed: {type(exc).__name__}; deterministic fallback")


def aggregate_inoculation_parameters(diagnoses: List[InoculationEncoding]) -> Dict[str, float]:
    if not diagnoses:
        return {}
    keys = [
        "inoculation_strength",
        "misinformation_decay",
        "resistance_growth",
        "trust_shift",
        "barrier_shift",
        "reactance_penalty",
        "trusted_messenger_fit",
        "misinformation_risk",
    ]
    output: Dict[str, float] = {}
    for key in keys:
        values = [item.intervention_parameters.get(key) for item in diagnoses if isinstance(item.intervention_parameters.get(key), (int, float))]
        if values:
            output[key] = round(sum(float(value) for value in values) / len(values), 3)
    output["mean_threat_recognition"] = round(sum(item.threat_recognition_score for item in diagnoses) / len(diagnoses), 3)
    output["mean_narrative_resilience"] = round(sum(item.narrative_resilience_score for item in diagnoses) / len(diagnoses), 3)
    output["booster_share"] = round(sum(1 for item in diagnoses if item.booster_needed) / len(diagnoses), 3)
    return output
