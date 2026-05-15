from sqlalchemy import Column, String, Float, Integer, Text, JSON
from .database import Base


class Narrative(Base):
    __tablename__ = "narratives"

    id = Column(String, primary_key=True, index=True)
    text = Column(Text)
    country = Column(String)
    admin_unit = Column(String)
    source_type = Column(String)


class EvidenceLedgerRecord(Base):
    __tablename__ = "evidence_ledger_records"

    narrative_id = Column(String, primary_key=True, index=True)
    text = Column(Text)
    evidence_route = Column(String, index=True)
    evidence_route_label = Column(String)
    country = Column(String, index=True)
    admin_unit = Column(String, index=True)
    admin_path = Column(Text)
    source_type = Column(String)
    source_name = Column(String)
    language = Column(String)
    period = Column(String)
    consent_tier = Column(String)
    visibility_tier = Column(String)
    sensitivity_level = Column(String)
    content_hash = Column(String, index=True)
    evidence_hash = Column(String, index=True)
    review_status = Column(String, index=True)
    reviewer_name = Column(String)
    reviewer_role = Column(String)
    review_reason = Column(Text)
    repository_bucket = Column(String, index=True)
    committed_at = Column(String, nullable=True)
    uncommit_history = Column(JSON)
    route_metadata = Column(JSON)
    governance = Column(JSON)
    created_at = Column(String, index=True)
    updated_at = Column(String, index=True)


class GovernanceLedgerEvent(Base):
    __tablename__ = "governance_ledger_events"

    id = Column(Integer, primary_key=True, index=True)
    event_hash = Column(String, index=True)
    previous_hash = Column(String)
    action = Column(String, index=True)
    detail = Column(Text)
    target_hash = Column(String)
    actor = Column(String)
    role = Column(String)
    occurred_at = Column(String, index=True)
    payload = Column(JSON)


class ValidationNarrative(Base):
    __tablename__ = "validation_narratives"

    narrative_id = Column(String, primary_key=True, index=True)
    text = Column(Text)
    route = Column(String)
    region = Column(String)
    expected_themes = Column(JSON)
    coder_a = Column(JSON)
    coder_b = Column(JSON)


class Encoding(Base):
    __tablename__ = "encodings"

    id = Column(Integer, primary_key=True, index=True)
    narrative_id = Column(String, index=True)
    themes = Column(JSON)
    sentiment = Column(Float)
    adoption_barrier_score = Column(Float)
    trust_score = Column(Float)
    confidence = Column(Float)


class SimulationRun(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    model_mode = Column(String)
    parameters = Column(JSON)
    result = Column(JSON)


class LearningFeedback(Base):
    __tablename__ = "learning_feedback"

    id = Column(Integer, primary_key=True, index=True)
    decision = Column(Text)
    outcome = Column(String, index=True)
    note = Column(Text)
    context = Column(JSON)
    created_at = Column(String, index=True)


class RetrainingJob(Base):
    __tablename__ = "retraining_jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, index=True)
    reason = Column(Text)
    metrics = Column(JSON)
    created_at = Column(String, index=True)
    completed_at = Column(String, nullable=True)


class BayesianPriorState(Base):
    __tablename__ = "bayesian_prior_state"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, index=True, default="global")
    version = Column(Integer, index=True)
    priors = Column(JSON)
    evidence_summary = Column(JSON)
    created_at = Column(String, index=True)
