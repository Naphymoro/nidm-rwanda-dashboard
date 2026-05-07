import os
from .schemas import EncodedNarrative, EncodingMode, NarrativeRecord
from .llm_prompts import NARRATIVE_ENCODING_SYSTEM_PROMPT, NARRATIVE_ENCODING_USER_TEMPLATE

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

client = (
    OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if OpenAI and os.getenv("OPENAI_API_KEY")
    else None
)


def encode_with_llm(record: NarrativeRecord) -> EncodedNarrative:
    if not client:
        return encode_rule_based(record)

    prompt = NARRATIVE_ENCODING_USER_TEMPLATE.format(text=record.text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": NARRATIVE_ENCODING_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    import json
    try:
        data = json.loads(response.choices[0].message.content)
    except Exception:
        return encode_rule_based(record)

    return EncodedNarrative(
        narrative_id=record.narrative_id,
        encoding_mode=EncodingMode.ai,
        themes=data.get("themes", ["general"]),
        sentiment=data.get("sentiment", 0.0),
        adoption_barrier_score=data.get("adoption_barrier_score", 0.5),
        trust_score=data.get("trust_score", 0.5),
        confidence=data.get("confidence", 0.5),
        model_notes="LLM encoding",
    )


def encode_rule_based(record: NarrativeRecord) -> EncodedNarrative:
    text = record.text.lower()
    themes = []

    if "cost" in text or "expensive" in text:
        themes.append("affordability")
    if "smoke" in text or "health" in text:
        themes.append("health")
    if "trust" in text or "believe" in text:
        themes.append("trust")
    if "wood" in text or "charcoal" in text or "fuel" in text:
        themes.append("fuel_access")

    return EncodedNarrative(
        narrative_id=record.narrative_id,
        encoding_mode=EncodingMode.manual,
        themes=themes or ["general"],
        sentiment=0.0,
        adoption_barrier_score=0.4,
        trust_score=0.6,
        confidence=0.5,
        model_notes="fallback rule-based",
    )


def encode_hybrid(record: NarrativeRecord) -> EncodedNarrative:
    encoded = encode_with_llm(record) if client else encode_rule_based(record)
    return encoded.model_copy(
        update={
            "encoding_mode": EncodingMode.hybrid,
            "reviewer_notes": "Hybrid mode: AI/fallback score prepared for human review before modelling.",
            "model_notes": f"{encoded.model_notes}; hybrid review layer",
        }
    )


def encode_narrative(record: NarrativeRecord, mode: EncodingMode = EncodingMode.ai) -> EncodedNarrative:
    if mode == EncodingMode.ai:
        return encode_with_llm(record)
    if mode == EncodingMode.hybrid:
        return encode_hybrid(record)
    return encode_rule_based(record)
