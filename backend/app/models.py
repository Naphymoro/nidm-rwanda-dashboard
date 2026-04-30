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
