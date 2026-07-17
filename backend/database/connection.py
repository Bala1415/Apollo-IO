import logging
import warnings
from backend.database.session import engine, SessionLocal, get_db

logger = logging.getLogger(__name__)

# Emit deprecation warning on import
warnings.warn(
    "backend.database.connection is deprecated. Use backend.database.session instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["engine", "SessionLocal", "get_db"]
