import jwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from backend.config import get_settings

logger = logging.getLogger("apollo.security.jwt")

# Default JWT algorithms
ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any], role: str) -> str:
    """
    Creates a short-lived JWT access token for a user or service.
    """
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.security.access_token_expire_minutes)
    
    # We must explicitly convert UUIDs or objects to strings
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    """
    Creates a long-lived JWT refresh token.
    """
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.security.refresh_token_expire_days)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, expected_type: str = "access") -> dict:
    """
    Verifies a JWT and ensures it has not expired and matches the expected type.
    Raises jwt.PyJWTError for invalid/expired tokens.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[ALGORITHM])
        
        # Verify token type (access vs refresh) to prevent misuse of tokens
        if payload.get("type") != expected_type:
            logger.warning(f"Token type mismatch. Expected {expected_type}, got {payload.get('type')}")
            raise jwt.InvalidTokenError("Invalid token type")
            
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug(f"Expired {expected_type} token presented.")
        raise
    except jwt.PyJWTError as e:
        logger.warning(f"Invalid {expected_type} token presented: {e}")
        raise
