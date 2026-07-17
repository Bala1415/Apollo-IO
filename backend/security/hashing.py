from passlib.context import CryptContext
import secrets
import hashlib

# Configure Passlib with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against the hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def generate_api_key() -> tuple[str, str]:
    """
    Generates a secure API key and its SHA-256 hash.
    Returns: (raw_key, key_hash)
    """
    raw_key = "ak_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash

def hash_api_key(raw_key: str) -> str:
    """Hashes a provided raw API key for database comparison."""
    return hashlib.sha256(raw_key.encode()).hexdigest()
