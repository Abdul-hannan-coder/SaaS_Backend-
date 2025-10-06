"""
User controller with functional approach for user management
"""
from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.user_model import UserSignUp, UserSignUpRequest, UserSignIn, UserResponse
from ..services.auth_service import verify_password, get_password_hash, create_access_token, get_current_user_from_token
from ..models.error_models import UserNotFoundError, UserAlreadyExistsError, DatabaseError, AuthenticationError
from ..services.user_service import (
    get_user_by_email, get_user_by_id, get_all_users,
    create_user, update_user, delete_user
)
from ....utils.database_dependency import get_database_session
from ....utils.my_logger import get_logger

logger = get_logger("USER_CONTROLLER")

security = HTTPBearer()
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_database_session)) -> UserSignUp:
    """Get current user from JWT token"""
    token = credentials.credentials
    email = get_current_user_from_token(token)
    if not email:
        raise AuthenticationError("Invalid authentication credentials", error_type="invalid")
    
    # Get user by email
    user = get_user_by_email(email, db)
    if not user:
        raise AuthenticationError("User not found", error_type="invalid")
    
    return user
def create_user_controller(user_data: UserSignUpRequest, db: Session) -> UserResponse:
    """Create a new user - HTTP layer only"""
    return create_user(user_data, db)

def authenticate_user(email: str, password: str, db: Session) -> Optional[UserSignUp]:
    """Authenticate user with email and password"""
    try:
        user = get_user_by_email(email, db)
        if not user:
            logger.warning(f"Authentication failed: user not found for email {email}")
            return None 
        
        if not verify_password(password, user.password):
            logger.warning(f"Authentication failed: invalid password for email {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: inactive user {email}")
            return None
        
        logger.info(f"User authenticated successfully: {email}")
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None

def login_user(user_data: UserSignIn, db: Session) -> dict:
    """Login user and return access token"""
    user = authenticate_user(user_data.email, user_data.password, db)
    if not user:
        raise AuthenticationError("Incorrect email or password", error_type="invalid")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    logger.info(f"User logged in successfully: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    }


def update_user_controller(user_id: str, user_data: dict, db: Session) -> UserResponse:
    """Update user information - HTTP layer only"""
    return update_user(user_id, user_data, db)

def delete_user_controller(user_id: str, db: Session) -> bool:
    """Delete user - HTTP layer only"""
    return delete_user(user_id, db) 