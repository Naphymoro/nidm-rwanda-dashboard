from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from .storage import sqlite_database_url


def default_database_url():
    if os.getenv("NDIM_DESKTOP") == "1" or os.getenv("NDIM_DATA_DIR"):
        return sqlite_database_url()
    return "sqlite:///./test.db"


DATABASE_URL = os.getenv("DATABASE_URL", default_database_url())

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
