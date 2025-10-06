"""
Google OAuth controller functions for handling authentication logic
"""
from fastapi import HTTPException, status
from sqlmodel import Session, select
from uuid import uuid4

from ....modules.login_logout.models.user_model import UserSignUp
from ....modules.login_logout.services.auth_service import create_access_token
from ....utils.my_logger import get_logger
from ..models.google_user_model import GoogleUserInfo, GoogleAuthResponse
from ..services.google_oauth_service import exchange_code_for_token, get_google_user_info

logger = get_logger("GOOGLE_AUTH_CONTROLLER")

async def handle_google_callback(code: str, db: Session) -> GoogleAuthResponse:
    """Handle Google OAuth callback and create/login user"""
    try:
        # Exchange code for token
        token_response = await exchange_code_for_token(code)
        
        # Get user info from Google
        google_user = await get_google_user_info(token_response.access_token)
        
        # Find or create user
        user = find_or_create_user(google_user, db)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.username})
        
        logger.info(f"Google authentication successful for user: {user.email}")
        
        return GoogleAuthResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "profile_picture": getattr(user, 'profile_picture', google_user.picture)
            }
        )
        
    except Exception as e:
        logger.error(f"Error in Google callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

def find_or_create_user(google_user: GoogleUserInfo, db: Session) -> UserSignUp:
    """Find existing user or create new one from Google profile"""
    try:
        # First, try to find user by email
        statement = select(UserSignUp).where(UserSignUp.email == google_user.email)
        existing_user = db.exec(statement).first()
        
        if existing_user:
            # Update Google-specific fields if they exist and are not set
            updated = False
            if hasattr(existing_user, 'google_id') and not getattr(existing_user, 'google_id', None):
                existing_user.google_id = google_user.id
                updated = True
            if hasattr(existing_user, 'profile_picture') and google_user.picture:
                existing_user.profile_picture = google_user.picture
                updated = True
            
            if updated:
                db.add(existing_user)
                db.commit()
                db.refresh(existing_user)
            
            logger.info(f"Found existing user: {existing_user.email}")
            return existing_user
        
        # Create new user
        username = generate_username_from_email(google_user.email, db)
        
        new_user = UserSignUp(
            id=uuid4(),
            email=google_user.email,
            username=username,
            full_name=google_user.name or google_user.email.split('@')[0],
            password="",  # No password for Google users
            is_active=True
        )
        
        # Add Google-specific fields if the model supports them
        if hasattr(new_user, 'google_id'):
            new_user.google_id = google_user.id
        if hasattr(new_user, 'auth_provider'):
            new_user.auth_provider = "google"
        if hasattr(new_user, 'profile_picture') and google_user.picture:
            new_user.profile_picture = google_user.picture
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Created new Google user: {new_user.email}")
        return new_user
        
    except Exception as e:
        logger.error(f"Error finding/creating user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user account"
        )

def generate_username_from_email(email: str, db: Session) -> str:
    """Generate unique username from email"""
    base_username = email.split('@')[0].lower()
    username = base_username
    counter = 1
    
    while True:
        statement = select(UserSignUp).where(UserSignUp.username == username)
        existing = db.exec(statement).first()
        if not existing:
            break
        username = f"{base_username}{counter}"
        counter += 1
    
    return username
