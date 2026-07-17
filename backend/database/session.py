import logging
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from backend.config import get_settings

logger = logging.getLogger(__name__)

# Retrieve configuration
settings = get_settings()

def get_engine():
    """
    Creates and configures the SQLAlchemy engine.
    """
    logger.info(f"Initializing database engine with pool_size={settings.db.pool_size}")
    return create_engine(
        settings.db.url,
        pool_size=settings.db.pool_size,
        pool_timeout=settings.db.connection_timeout,
        pool_pre_ping=True,
        echo=settings.app.debug
    )

engine = get_engine()

# Global session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Scoped session for thread-safe operations in complex workflows
ScopedSession = scoped_session(SessionLocal)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Dependency to yield a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def transaction() -> Generator[Session, None, None]:
    """
    Context manager for explicit transaction management.
    Handles commit on success and rollback on exception.
    """
    db = SessionLocal()
    try:
        logger.debug("Transaction started.")
        yield db
        db.commit()
        logger.debug("Transaction committed.")
    except Exception as e:
        logger.error(f"Transaction failed, rolling back. Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
