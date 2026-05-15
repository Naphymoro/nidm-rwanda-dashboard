from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EncodingMode(str, Enum):
    manual = "manual"
    ai = "ai"
    hybrid = "hybrid"


class ModelMode(str, Enum):
    compartmental = "compartmental"
    agent_based = "agent_based"
    hybrid = "hybrid"


class NarrativeMetadata(BaseModel):
    source_type: str = Field(description="text, csv, pdf, api, field_note")
    source_name: Optional[str] = None
    country: Optional[str] = None
    admin_level: Optional[str] = None
    admin_unit: Optional[str] = None
    language: Optional[str] = "en"
    provenance: Dict[str, Any] = Field(default_factory=dict)


class NarrativeRecord(BaseModel):
    narrative_id: str
    text: str
    metadata: NarrativeMetadata
    tags: List[str] = Field(default_factory=list)


class EncodedNarrative(BaseModel):
    narrative_id: str
    encoding_mode: EncodingMode
    themes: List[str] = Field(default_factory=list)
    sentiment: Optional[float] = Field(default=None, ge=-1, le=1)
    adoption_barrier_score: Optional[float] = Field(default=None, ge=0, le=1)
    trust_score: Optional[float] = Field(default=None, ge=0, le=1)
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    reviewer_notes: Optional[str] = None
    model_notes: Optional[str] = None


class InoculationEncoding(BaseModel):
    narrative_id: str
    diagnosis_mode: str = "heuristic"
    narrative_type: str = "adoption_narrative"
    threat_type: str = "none_detected"
    misinformation_mechanism: str = "none_detected"
    source_actor: Optional[str] = None
    susceptible_group: Optional[str] = None
    psychological_trigger: Optional[str] = None
    threat_recognition_score: float = Field(default=0.0, ge=0, le=1)
    misinformation_risk_score: float = Field(default=0.0, ge=0, le=1)
    identity_threat_score: float = Field(default=0.0, ge=0, le=1)
    reactance_risk_score: float = Field(default=0.0, ge=0, le=1)
    cultural_sensitivity_score: float = Field(default=0.0, ge=0, le=1)
    refutability_score: float = Field(default=0.0, ge=0, le=1)
    trusted_messenger: str = "local peer demonstrator"
    trusted_messenger_fit_score: float = Field(default=0.0, ge=0, le=1)
    weak_dose_claim: str = ""
    refutational_preemption: str = ""
    counter_narrative: str = ""
    booster_strategy: str = ""
    booster_needed: bool = False
    narrative_resilience_score: float = Field(default=0.0, ge=0, le=1)
    confidence: float = Field(default=0.0, ge=0, le=1)
    evidence_spans: Dict[str, Optional[str]] = Field(default_factory=dict)
    intervention_parameters: Dict[str, float] = Field(default_factory=dict)
    human_review_status: str = "requires_review"
    model_notes: Optional[str] = None


class SimulationRequest(BaseModel):
    model_mode: ModelMode = ModelMode.hybrid
    country: str = "Rwanda"
    admin_unit: Optional[str] = None
    horizon_days: int = Field(default=180, ge=1, le=3650)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SimulationResult(BaseModel):
    model_mode: ModelMode
    trajectory: List[Dict[str, float]]
    assumptions: Dict[str, Any]
