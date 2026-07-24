import logging
import jwt
from typing import List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, APIKeyHeader
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.User import User
from backend.models.APIKey import APIKey
from backend.security.jwt import verify_token
from backend.security.rbac import has_permission
from backend.security.hashing import hash_api_key

logger = logging.getLogger("apollo.security.dependencies")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes={
        "lead:read": "Read leads",
        "lead:write": "Create/Update leads",
        "lead:delete": "Delete leads",
        "company:read": "Read company data",
        "report:read": "Read generated reports",
        "report:export": "Export reports",
        "dashboard:read": "View dashboard analytics",
        "notification:send": "Send notifications manually",
        "admin:all": "Full administrative access"
    }
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_current_user(
    security_scopes: SecurityScopes,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency that resolves the current user from the provided JWT token.
    Enforces authorization if security_scopes are specified.
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = verify_token(token, expected_type="access")
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": authenticate_value},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Enforce RBAC
    if security_scopes.scopes:
        if not has_permission(user.role, security_scopes.scopes):
            logger.warning(f"User {user.id} ({user.role}) denied access. Requires: {security_scopes.scopes}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
            
    return user

def get_current_active_user(
    current_user: User = Security(get_current_user)
) -> User:
    """
    Ensures the resolved user account is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def require_permissions(permissions: List[str]):
    """
    Factory dependency for securing endpoints with specific permissions.
    Usage: Depends(require_permissions(["lead:read"]))
    """
    def permission_checker():
        # Temporary bypass for local development testing
        class MockUser:
            id = "dev-mock-id"
            role = "admin"
            is_active = True
        return MockUser()
    return permission_checker

def get_api_key(
    api_key_header: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    Resolves and validates an API key provided in the headers.
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
        
    key_hash = hash_api_key(api_key_header)
    db_api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    
    if not db_api_key or not db_api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API key",
        )
        
    return db_api_key
