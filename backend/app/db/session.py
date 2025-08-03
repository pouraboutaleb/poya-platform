from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from .base_class import Base

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/mrdpol_core_db"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Enable automatic reconnection
    pool_size=5,  # Default connection pool size
    max_overflow=10  # Allow up to 10 connections beyond pool_size
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
