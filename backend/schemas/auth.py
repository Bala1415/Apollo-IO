import uuid
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class Token(BaseModel):
    """Schema for OAuth2 token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenPayload(BaseModel):
    """Schema for decoding JWT claims."""
    sub: str
    role: str
    exp: int

class UserBase(BaseModel):
    """Base user attributes."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """Schema for traditional email/password login."""
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """Schema for user responses."""
    id: uuid.UUID
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class APIKeyCreate(BaseModel):
    """Schema for requesting a new API Key."""
    name: str = Field(..., max_length=100)
    expires_in_days: Optional[int] = None

class APIKeyResponse(BaseModel):
    """Schema for returning a generated API Key."""
    id: uuid.UUID
    name: str
    api_key: str  # Only returned once during creation
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
