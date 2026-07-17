import logging
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.User import User
from backend.models.APIKey import APIKey
from backend.schemas.auth import Token, UserCreate, UserResponse, APIKeyCreate, APIKeyResponse
from backend.schemas.response import StandardResponse, success_response, error_response
from backend.security.hashing import get_password_hash, verify_password, generate_api_key
from backend.security.jwt import create_access_token, create_refresh_token
from backend.security.dependencies import get_current_active_user
from backend.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger("apollo.api.auth")

@router.post("/register", response_model=StandardResponse[UserResponse])
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user account.
    """
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
        
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role="Viewer" # Default safe role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Registered new user: {user.email}")
    return success_response(data=user, message="Registration successful.")

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, getting an access token for future requests.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
        
    access_token = create_access_token(subject=str(user.id), role=user.role)
    refresh_token = create_refresh_token(subject=str(user.id))
    
    settings = get_settings()
    
    logger.info(f"User {user.email} logged in successfully.")
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.security.access_token_expire_minutes * 60
    )

@router.post("/api-keys", response_model=StandardResponse[APIKeyResponse])
async def create_new_api_key(
    req: APIKeyCreate,
    current_user: User = Security(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generates a new API key for the current user.
    The raw key is returned exactly once.
    """
    raw_key, key_hash = generate_api_key()
    
    api_key = APIKey(
        key_hash=key_hash,
        name=req.name,
        user_id=current_user.id
        # expires_at could be set here
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    # We construct a synthetic response model since `api_key` only exists in memory
    response_data = APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        api_key=raw_key,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at
    )
    
    logger.info(f"API Key '{req.name}' generated for user {current_user.email}.")
    return success_response(data=response_data, message="API Key created successfully. Store it securely; it will not be shown again.")
