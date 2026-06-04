from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from .storage import sqlite_database_url


def default_database_url():
    if os.getenv("NDIM_DESKTOP") == "1" or os.getenv("NDIM_DATA_DIR"):
        return sqlite_database_url()
    return "sqlite:///./test.db"


def normalized_database_url() -> str:
    raw = os.getenv("DATABASE_URL") or ""
    if os.getenv("NDIM_REQUIRE_DATABASE") == "1" and not raw:
        raise RuntimeError("NDIM_REQUIRE_DATABASE=1 requires DATABASE_URL for hosted deployments.")
    if not raw:
        return default_database_url()
    if raw.startswith("postgres://"):
        return raw.replace("postgres://", "postgresql+psycopg://", 1)
    if raw.startswith("postgresql://") and "+psycopg" not in raw.split("://", 1)[0]:
        return raw.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw


DATABASE_URL = normalized_database_url()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
