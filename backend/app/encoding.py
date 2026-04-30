from .schemas import EncodedNarrative, EncodingMode, NarrativeRecord


def encode_narrative(record: NarrativeRecord, mode: EncodingMode = EncodingMode.ai) -> EncodedNarrative:
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

    barrier_score = 0.6 if "cost" in text or "expensive" in text else 0.3
    trust_score = 0.4 if "trust" in text or "believe" in text else 0.7

    return EncodedNarrative(
        narrative_id=record.narrative_id,
        encoding_mode=mode,
        themes=themes or ["general"],
        sentiment=0.0,
        adoption_barrier_score=barrier_score,
        trust_score=trust_score,
        confidence=0.55,
        model_notes="Rule-based baseline encoder. Replace or augment with LLM encoder in production.",
    )
