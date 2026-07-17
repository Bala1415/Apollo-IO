import pytest
from backend.security.hashing import get_password_hash, verify_password, generate_api_key, hash_api_key
from backend.security.rbac import has_permission, Permissions
from backend.security.jwt import create_access_token, verify_token
import jwt

@pytest.mark.unit
def test_password_hashing():
    """Verify that password hashing correctly obscures and validates."""
    password = "super_secure_password123!"
    hashed = get_password_hash(password)
    
    assert password != hashed
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

@pytest.mark.unit
def test_api_key_generation():
    """Verify API keys generate securely and hash deterministically."""
    raw_key, key_hash = generate_api_key()
    
    assert raw_key.startswith("ak_")
    assert len(raw_key) > 20
    assert hash_api_key(raw_key) == key_hash

@pytest.mark.unit
def test_rbac_engine():
    """Verify that roles map correctly to permissions."""
    # Admin has all permissions including Administration
    assert has_permission("Admin", [Permissions.LEAD_READ]) is True
    assert has_permission("Admin", [Permissions.ADMINISTRATION]) is True
    
    # Analyst cannot delete leads or send notifications
    assert has_permission("Analyst", [Permissions.LEAD_READ]) is True
    assert has_permission("Analyst", [Permissions.LEAD_DELETE]) is False
    assert has_permission("Analyst", [Permissions.NOTIFICATION_SEND]) is False
    
    # Viewer can only read
    assert has_permission("Viewer", [Permissions.LEAD_READ]) is True
    assert has_permission("Viewer", [Permissions.LEAD_WRITE]) is False

@pytest.mark.unit
def test_jwt_lifecycle():
    """Verify JWT creation and validation."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    role = "Sales"
    
    token = create_access_token(subject=user_id, role=role)
    assert token is not None
    
    # Validate payload
    payload = verify_token(token, expected_type="access")
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert payload["type"] == "access"

@pytest.mark.unit
def test_jwt_invalid_type():
    """Verify JWT rejects wrong token types."""
    token = create_access_token(subject="123", role="Viewer")
    
    with pytest.raises(jwt.InvalidTokenError):
        verify_token(token, expected_type="refresh")
