from sqlalchemy import Column, String, Float, Integer, Text, JSON
from .database import Base


class Narrative(Base):
    __tablename__ = "narratives"

    id = Column(String, primary_key=True, index=True)
    text = Column(Text)
    country = Column(String)
    admin_unit = Column(String)
    source_type = Column(String)


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
