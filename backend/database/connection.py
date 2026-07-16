import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Load database URL from environment variable, fallback to localhost for development
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/apollo_db"
)

# Initialize SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection pool pre-ping
    echo=False
)

# Session factory for creating new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """
    Dependency to yield database sessions for FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
