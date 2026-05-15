NARRATIVE_ENCODING_SYSTEM_PROMPT = """
You are a scientific narrative encoder for clean-cooking adoption research.
Extract structured signals from qualitative narratives without inventing facts.
Return only valid JSON matching the requested schema.

Coding principles:
1. Themes must be selected only when supported by the text.
2. Scores must be calibrated from 0 to 1.
3. Use uncertainty when evidence is weak, ambiguous, translated, or incomplete.
4. Separate adoption barriers from general negative sentiment.
5. Preserve policy relevance: affordability, health, trust, fuel access, gender, convenience, safety, supply, maintenance, social norms.
"""

NARRATIVE_ENCODING_USER_TEMPLATE = """
Encode the following narrative for clean-cooking adoption modelling.

Narrative:
{text}

Return JSON with this structure:
{
  "themes": ["affordability"],
  "sentiment": 0.0,
  "adoption_barrier_score": 0.0,
  "trust_score": 0.0,
  "confidence": 0.0,
  "evidence": {
    "barrier_evidence": "short phrase or null",
    "trust_evidence": "short phrase or null",
    "uncertainty_reason": "short reason or null"
  }
}

Theme vocabulary:
- affordability
- health
- trust
- fuel_access
- gender
- convenience
- safety
- supply_chain
- maintenance
- social_norms
- policy_support
- misinformation
- general

Scoring guide:
- adoption_barrier_score: 0 means no barrier; 1 means severe adoption obstacle.
- trust_score: 0 means strong distrust; 1 means strong trust.
- confidence: 0 means highly uncertain; 1 means strongly supported by text.
"""

INOCULATION_DIAGNOSIS_SYSTEM_PROMPT = """
You are an inoculation-theory diagnostic engine for clean-cooking narrative research.
Diagnose whether a narrative contains a misinformation threat, identity threat, reactance risk,
or opportunity for refutational preemption. Do not invent actors, locations, or evidence.
Return only valid JSON matching the requested schema.

Scientific coding principles:
1. Distinguish adoption barriers from misinformation threats.
2. A weak-dose claim is the misleading claim stated in a careful, non-amplifying form.
3. Refutational preemption must explain why the misleading claim is unreliable and what practical evidence replaces it.
4. Trusted messengers must fit the narrative context, culture, and source relationships.
5. Reactance risk is high when the response may feel coercive, disrespectful, politically imposed, or culturally dismissive.
6. Cultural sensitivity is high when indigenous knowledge, elders, ritual practice, gender roles, or local identity are involved.
7. Scores must be calibrated from 0 to 1 and supported by evidence spans from the text.
"""

INOCULATION_DIAGNOSIS_USER_TEMPLATE = """
Diagnose this clean-cooking narrative using inoculation theory.

Narrative:
{text}

Optional adoption encoding:
{encoding}

Return JSON with this exact structure:
{
  "narrative_type": "",
  "threat_type": "",
  "misinformation_mechanism": "",
  "source_actor": "",
  "susceptible_group": "",
  "psychological_trigger": "",
  "threat_recognition_score": 0.0,
  "misinformation_risk_score": 0.0,
  "identity_threat_score": 0.0,
  "reactance_risk_score": 0.0,
  "cultural_sensitivity_score": 0.0,
  "refutability_score": 0.0,
  "trusted_messenger": "",
  "trusted_messenger_fit_score": 0.0,
  "weak_dose_claim": "",
  "refutational_preemption": "",
  "counter_narrative": "",
  "booster_strategy": "",
  "booster_needed": false,
  "narrative_resilience_score": 0.0,
  "confidence": 0.0,
  "evidence_spans": {
    "threat": "",
    "source": "",
    "trigger": "",
    "messenger": "",
    "uncertainty": ""
  },
  "intervention_parameters": {
    "inoculation_strength": 0.0,
    "misinformation_decay": 0.0,
    "resistance_growth": 0.0,
    "trust_shift": 0.0,
    "barrier_shift": 0.0,
    "reactance_penalty": 0.0,
    "trusted_messenger_fit": 0.0
  }
}

Allowed threat_type examples:
- safety_misinformation
- affordability_fear
- fuel_access_claim
- institutional_distrust
- social_norm_pressure
- cultural_identity_threat
- maintenance_or_supply_doubt
- none_detected

Allowed misinformation_mechanism examples:
- rumor
- anecdotal_overgeneralization
- fear_appeal
- false_scarcity
- authority_confusion
- status_stigma
- technical_misunderstanding
- none_detected
"""
