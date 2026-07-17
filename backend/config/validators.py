from typing import List, Union
from pydantic import AnyHttpUrl, AnyUrl
import re

def validate_cors_origins(v: Union[str, List[str]]) -> List[str]:
    """
    Validates and normalizes CORS origins.
    Accepts a single string (comma-separated), a list of strings, or '*'
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError("Invalid CORS origins format")

def validate_database_url(v: str) -> str:
    """
    Validates the database URL to ensure it has the correct prefix for async/sync drivers
    if necessary, or simply ensures it's a valid URI.
    """
    if not v:
        return v
    if v.startswith("postgres://"):
        return v.replace("postgres://", "postgresql://", 1)
    return v

def validate_api_key(v: str) -> str:
    """
    Basic validation to ensure API keys are not accidentally left as empty strings
    or default placeholder values in production.
    """
    if v in ("your_api_key_here", "dummy_key", ""):
        raise ValueError("Invalid or placeholder API key detected")
    return v
