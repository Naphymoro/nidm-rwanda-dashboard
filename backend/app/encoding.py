import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from .schemas import EncodedNarrative, EncodingMode, NarrativeRecord
from .llm_prompts import NARRATIVE_ENCODING_SYSTEM_PROMPT, NARRATIVE_ENCODING_USER_TEMPLATE

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


PROVIDER_DEFAULTS: Dict[str, Dict[str, Optional[str]]] = {
    "openai": {"env": "OPENAI_API_KEY", "model": "gpt-4o-mini", "base_url": None},
    "azure-openai": {"env": "AZURE_OPENAI_API_KEY", "model": "gpt-4o-mini", "base_url": "AZURE_OPENAI_ENDPOINT"},
    "openrouter": {"env": "OPENROUTER_API_KEY", "model": "openai/gpt-4o-mini", "base_url": "https://openrouter.ai/api/v1"},
    "mistral": {"env": "MISTRAL_API_KEY", "model": "mistral-small-latest", "base_url": "https://api.mistral.ai/v1"},
    "anthropic": {"env": "ANTHROPIC_API_KEY", "model": "claude-3-5-haiku-latest", "base_url": "https://api.anthropic.com/v1/messages"},
    "gemini": {"env": "GEMINI_API_KEY", "model": "gemini-1.5-flash", "base_url": "https://generativelanguage.googleapis.com/v1beta"},
    "ollama": {"env": None, "model": "llama3.1", "base_url": "http://127.0.0.1:11434/api/chat"},
    "lmstudio": {"env": None, "model": "local-model", "base_url": "http://127.0.0.1:1234/v1"},
    "openai-compatible": {"env": "OPENAI_COMPATIBLE_API_KEY", "model": "local-model", "base_url": "OPENAI_COMPATIBLE_BASE_URL"},
    "local": {"env": None, "model": "llama3.1", "base_url": "http://127.0.0.1:11434/api/chat"},
    "deterministic": {"env": None, "model": "rule-based", "base_url": None},
}


def supported_llm_providers() -> Dict[str, Dict[str, Optional[str]]]:
    return PROVIDER_DEFAULTS


def normalize_provider(provider: Optional[str]) -> str:
    value = (provider or "openai").strip().lower()
    return value if value in PROVIDER_DEFAULTS else "openai-compatible"


def _default_base_url(provider: str) -> Optional[str]:
    raw = PROVIDER_DEFAULTS[provider].get("base_url")
    if raw and raw.endswith("_URL") or raw == "AZURE_OPENAI_ENDPOINT":
        return os.getenv(raw or "")
    return raw


def _provider_key(provider: str, api_key: Optional[str]) -> Optional[str]:
    if api_key:
        return api_key
    env_name = PROVIDER_DEFAULTS[provider].get("env")
    return os.getenv(env_name) if env_name else None


def llm_provider_status(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    normalized = normalize_provider(provider)
    key = _provider_key(normalized, api_key)
    endpoint = base_url or _default_base_url(normalized)
    model_name = model or PROVIDER_DEFAULTS[normalized].get("model")
    local_provider = normalized in {"ollama", "lmstudio", "local", "deterministic"}
    configured = normalized == "deterministic" or local_provider or bool(key) or (normalized == "openai-compatible" and bool(endpoint))
    return {
        "provider": normalized,
        "model": model_name,
        "base_url_configured": bool(endpoint),
        "api_key_configured": bool(key),
        "credential_source": "session" if api_key else "environment" if key else "not_required" if local_provider else "endpoint_no_key" if normalized == "openai-compatible" and endpoint else "missing",
        "configured": configured,
    }


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if "\n" in cleaned:
            cleaned = cleaned.split("\n", 1)[1]
    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def _encoded_from_data(record: NarrativeRecord, data: Dict[str, Any], mode: EncodingMode, note: str) -> EncodedNarrative:
    return EncodedNarrative(
        narrative_id=record.narrative_id,
        encoding_mode=mode,
        themes=data.get("themes", ["general"]),
        sentiment=data.get("sentiment", 0.0),
        adoption_barrier_score=data.get("adoption_barrier_score", 0.5),
        trust_score=data.get("trust_score", 0.5),
        confidence=data.get("confidence", 0.5),
        model_notes=note,
    )


def encode_rule_based(
    record: NarrativeRecord,
    mode: EncodingMode = EncodingMode.manual,
    note: str = "deterministic heuristic fallback",
) -> EncodedNarrative:
    text = record.text.lower()
    provenance = record.metadata.provenance or {}
    tag_text = " ".join(str(tag).lower() for tag in (record.tags or []))
    route = str(provenance.get("evidence_mode") or record.metadata.source_type or "").lower()

    def hits(words: list[str]) -> int:
        return sum(len(re.findall(rf"\b{re.escape(word)}\b", text)) for word in words)

    def clamp(value: float, low: float = 0.05, high: float = 0.95) -> float:
        return max(low, min(high, value))

    affordability = hits(["cost", "costly", "expensive", "price", "money", "loan", "subsidy", "afford", "market", "installment", "saving", "payment"])
    fuel_access = hits(["wood", "firewood", "charcoal", "fuel", "lpg", "electricity", "pellet", "repair", "spare", "vendor", "maintenance", "warranty"])
    safety = hits(["safe", "unsafe", "explode", "explosion", "burn", "pressure", "danger", "risk"])
    habit = hits(["habit", "tradition", "always", "used", "taste", "family", "husband", "mother", "routine", "custom", "usual"])
    health = hits(["smoke", "cough", "eyes", "chest", "health", "clinic", "child", "children", "hospital", "breathing"])
    trust_positive = hits(["trust", "trusted", "believe", "demonstration", "showed", "trained", "health worker", "leader", "technician", "neighbour", "neighbor", "cooperative"])
    trust_negative = hits(["distrust", "fake", "cheated", "broken", "failed", "rumor", "rumour", "doubt", "fear", "unsafe"])
    misinformation = hits(["rumor", "rumour", "misleading", "claim", "heard", "explode", "poison", "witchcraft", "dangerous", "false", "myth"])
    social = hits(["people", "neighbour", "neighbor", "group", "church", "cooperative", "women", "village", "leader", "family", "peer", "meeting", "market"])
    emotion = hits(["worried", "afraid", "fear", "proud", "relieved", "tired", "angry", "hope", "happy", "regret", "ashamed", "stress", "confident"])
    positive_stance = hits(["saved", "save", "faster", "less smoke", "clean", "convenient", "helped", "adopt", "try", "benefit", "accepted", "liked"])
    negative_stance = hits(["not use", "refuse", "stopped", "avoid", "cannot", "can't", "too expensive", "unsafe", "difficult", "rejected", "against"])
    local_grounding = hits(["district", "sector", "village", "market", "cell", "province", "community", "home"])
    if "for" in tag_text:
        positive_stance += 1
    if "against" in tag_text:
        negative_stance += 1
    if "mixed" in tag_text:
        positive_stance += 1
        negative_stance += 1
    if "indigenous" in route:
        local_grounding += 2
        confidence_bonus = 0.04
    elif "citizen" in route or "social" in route:
        confidence_bonus = -0.03
    else:
        confidence_bonus = 0.0
    if record.metadata.country:
        local_grounding += 1
    if record.metadata.admin_unit:
        local_grounding += 1
    if provenance.get("question_title") or provenance.get("evidence_mode_label"):
        local_grounding += 1

    themes = []
    theme_scores = {
        "affordability": affordability,
        "fuel_access": fuel_access,
        "safety": safety,
        "habit": habit,
        "health": health,
        "trust": trust_positive + max(0, trust_negative - 1),
        "inoculation": misinformation + safety,
        "social_influence": social,
        "local_grounding": local_grounding,
    }
    for theme, score in theme_scores.items():
        if score > 0:
            themes.append(theme)

    barrier_pressure = affordability * 0.095 + fuel_access * 0.075 + safety * 0.07 + habit * 0.055 + negative_stance * 0.06 + misinformation * 0.025
    barrier_relief = positive_stance * 0.035 + health * 0.015
    barrier = clamp(0.30 + barrier_pressure - barrier_relief)

    trust = clamp(0.48 + trust_positive * 0.060 + health * 0.025 + social * 0.010 + local_grounding * 0.018 - trust_negative * 0.070 - misinformation * 0.025)
    confidence = clamp(0.38 + confidence_bonus + min(local_grounding, 5) * 0.045 + min(len(text.split()), 140) / 1150 + min(len(themes), 6) * 0.025)
    sentiment = clamp((positive_stance + trust_positive + health * 0.4 + emotion * 0.12 - negative_stance - trust_negative - safety * 0.2 - misinformation * 0.15) / 10, -0.8, 0.8)

    return EncodedNarrative(
        narrative_id=record.narrative_id,
        encoding_mode=mode,
        themes=themes or ["general"],
        sentiment=sentiment,
        adoption_barrier_score=round(barrier, 3),
        trust_score=round(trust, 3),
        confidence=round(confidence, 3),
        model_notes=(
            f"{note}; transparent content-sensitive heuristic used because no confirmed LLM result was available. "
            f"signals: barrier_terms={affordability + fuel_access + safety + habit}, trust_positive={trust_positive}, "
            f"trust_negative={trust_negative}, misinformation={misinformation}, emotion={emotion}, social={social}, "
            f"stance_tags={tag_text or 'none'}, local_grounding={local_grounding}"
        ),
    )


def _chat_payload(record: NarrativeRecord) -> list[dict[str, str]]:
    prompt = NARRATIVE_ENCODING_USER_TEMPLATE.format(text=record.text)
    return [
        {"role": "system", "content": NARRATIVE_ENCODING_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]


def _encode_openai_compatible(
    record: NarrativeRecord,
    mode: EncodingMode,
    provider: str,
    api_key: Optional[str],
    base_url: Optional[str],
    model: Optional[str],
) -> EncodedNarrative:
    if not OpenAI:
        return encode_rule_based(record, mode, f"{provider} SDK unavailable; deterministic fallback")
    status = llm_provider_status(provider, api_key, base_url, model)
    key = _provider_key(status["provider"], api_key)
    if not key and status["provider"] not in {"lmstudio", "openai-compatible"}:
        return encode_rule_based(record, mode, f"{status['provider']} key missing; deterministic fallback")
    client_kwargs: Dict[str, Any] = {"api_key": key or "local"}
    endpoint = base_url or _default_base_url(status["provider"])
    if endpoint:
        client_kwargs["base_url"] = endpoint
    client = OpenAI(**client_kwargs)
    response = client.chat.completions.create(
        model=status["model"],
        messages=_chat_payload(record),
        temperature=0.2,
    )
    data = _extract_json(response.choices[0].message.content or "{}")
    return _encoded_from_data(record, data, mode, f"{status['provider']} LLM encoding; credential_source={status['credential_source']}")


def _post_json(url: str, body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def _encode_anthropic(record: NarrativeRecord, mode: EncodingMode, api_key: Optional[str], model: Optional[str]) -> EncodedNarrative:
    key = _provider_key("anthropic", api_key)
    if not key:
        return encode_rule_based(record, mode, "anthropic key missing; deterministic fallback")
    body = {
        "model": model or PROVIDER_DEFAULTS["anthropic"]["model"],
        "max_tokens": 900,
        "temperature": 0.2,
        "system": NARRATIVE_ENCODING_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": NARRATIVE_ENCODING_USER_TEMPLATE.format(text=record.text)}],
    }
    result = _post_json(
        PROVIDER_DEFAULTS["anthropic"]["base_url"] or "",
        body,
        {"x-api-key": key, "anthropic-version": "2023-06-01"},
    )
    content = "".join(part.get("text", "") for part in result.get("content", []) if isinstance(part, dict))
    return _encoded_from_data(record, _extract_json(content), mode, "anthropic LLM encoding; credential_source=session_or_environment")


def _encode_gemini(record: NarrativeRecord, mode: EncodingMode, api_key: Optional[str], model: Optional[str], base_url: Optional[str]) -> EncodedNarrative:
    key = _provider_key("gemini", api_key)
    if not key:
        return encode_rule_based(record, mode, "gemini key missing; deterministic fallback")
    model_name = model or PROVIDER_DEFAULTS["gemini"]["model"]
    root = (base_url or PROVIDER_DEFAULTS["gemini"]["base_url"] or "").rstrip("/")
    url = f"{root}/models/{model_name}:generateContent?key={key}"
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{NARRATIVE_ENCODING_SYSTEM_PROMPT}\n\n{NARRATIVE_ENCODING_USER_TEMPLATE.format(text=record.text)}"}],
            }
        ],
        "generationConfig": {"temperature": 0.2},
    }
    result = _post_json(url, body, {})
    text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return _encoded_from_data(record, _extract_json(text), mode, "gemini LLM encoding; credential_source=session_or_environment")


def _encode_ollama(record: NarrativeRecord, mode: EncodingMode, provider: str, base_url: Optional[str], model: Optional[str]) -> EncodedNarrative:
    endpoint = base_url or _default_base_url(provider) or PROVIDER_DEFAULTS["ollama"]["base_url"]
    model_name = model or PROVIDER_DEFAULTS[provider]["model"]
    body = {
        "model": model_name,
        "messages": _chat_payload(record),
        "stream": False,
        "options": {"temperature": 0.2},
    }
    result = _post_json(endpoint or "", body, {})
    text = result.get("message", {}).get("content", "")
    return _encoded_from_data(record, _extract_json(text), mode, f"{provider} local LLM encoding")


def encode_with_llm(
    record: NarrativeRecord,
    mode: EncodingMode = EncodingMode.ai,
    provider: Optional[str] = "openai",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> EncodedNarrative:
    normalized = normalize_provider(provider)
    if normalized == "deterministic":
        return encode_rule_based(record, mode, "deterministic fallback selected")
    try:
        if normalized == "anthropic":
            return _encode_anthropic(record, mode, api_key, model)
        if normalized == "gemini":
            return _encode_gemini(record, mode, api_key, model, base_url)
        if normalized in {"ollama", "local"}:
            return _encode_ollama(record, mode, normalized, base_url, model)
        return _encode_openai_compatible(record, mode, normalized, api_key, base_url, model)
    except (json.JSONDecodeError, urllib.error.URLError, TimeoutError, Exception) as exc:
        return encode_rule_based(record, mode, f"{normalized} failed: {type(exc).__name__}; deterministic fallback")


def encode_hybrid(
    record: NarrativeRecord,
    provider: Optional[str] = "openai",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> EncodedNarrative:
    encoded = encode_with_llm(record, EncodingMode.hybrid, provider, api_key, base_url, model)
    return encoded.model_copy(
        update={
            "encoding_mode": EncodingMode.hybrid,
            "reviewer_notes": "Hybrid mode: LLM/fallback score prepared for human review before modelling.",
            "model_notes": f"{encoded.model_notes}; hybrid review layer",
        }
    )


def encode_narrative(
    record: NarrativeRecord,
    mode: EncodingMode = EncodingMode.ai,
    provider: Optional[str] = "openai",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> EncodedNarrative:
    if mode == EncodingMode.ai:
        return encode_with_llm(record, EncodingMode.ai, provider, api_key, base_url, model)
    if mode == EncodingMode.hybrid:
        return encode_hybrid(record, provider, api_key, base_url, model)
    return encode_rule_based(record, EncodingMode.manual)
