"""
Gemini API key service - handles all database operations and business logic
"""
from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from .model import (
    GeminiKey, 
    GeminiKeyCreate, 
    GeminiKeyUpdate, 
    GeminiKeyResponse, 
    GeminiKeyStatus
)
from .error_models import (
    GeminiKeyNotFoundError, 
    GeminiKeyAlreadyExistsError, 
    GeminiKeyInvalidError,
    DatabaseError,
    ValidationError
)
from ....utils.my_logger import get_logger

logger = get_logger("GEMINI_KEY_SERVICE")

# Core service functions - simplified and consolidated

def create_gemini_key(user_id: UUID, api_key: str, db: Session) -> GeminiKeyResponse:
    """Create a new Gemini API key with business logic validation"""
    # Validate API key format
    if not api_key or len(api_key.strip()) < 10:
        raise ValidationError("Invalid API key format", field="api_key", error_type="invalid_api_key")
    
    # Check if user already has a key
    existing_key = db.exec(select(GeminiKey).where(GeminiKey.user_id == user_id)).first()
    if existing_key:
        raise GeminiKeyAlreadyExistsError("User already has a Gemini API key", user_id=str(user_id))
    
    # Database operations
    try:
        gemini_key = GeminiKey(
            user_id=user_id,
            api_key=api_key.strip()
        )
        
        db.add(gemini_key)
        db.commit()
        db.refresh(gemini_key)
        
        logger.info(f"Gemini API key created successfully for user {user_id}")
        
        return GeminiKeyResponse(
            id=gemini_key.id,
            user_id=gemini_key.user_id,
            api_key_preview=_get_key_preview(gemini_key.api_key),
            is_active=gemini_key.is_active,
            created_at=gemini_key.created_at,
            updated_at=gemini_key.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error creating Gemini API key: {str(e)}", operation="create_gemini_key", error_type="transaction")

def get_gemini_key(user_id: UUID, db: Session) -> Optional[GeminiKeyResponse]:
    """Get Gemini API key for a user"""
    try:
        gemini_key = db.exec(select(GeminiKey).where(GeminiKey.user_id == user_id)).first()
        
        if not gemini_key:
            return None
        
        return GeminiKeyResponse(
            id=gemini_key.id,
            user_id=gemini_key.user_id,
            api_key_preview=_get_key_preview(gemini_key.api_key),
            is_active=gemini_key.is_active,
            created_at=gemini_key.created_at,
            updated_at=gemini_key.updated_at
        )
        
    except Exception as e:
        raise DatabaseError(f"Error fetching Gemini API key: {str(e)}", operation="get_gemini_key", error_type="query")

def update_gemini_key(user_id: UUID, api_key: Optional[str] = None, is_active: Optional[bool] = None, db: Session = None) -> Optional[GeminiKeyResponse]:
    """Update Gemini API key for a user"""
    gemini_key = db.exec(select(GeminiKey).where(GeminiKey.user_id == user_id)).first()
    
    if not gemini_key:
        return None
    
    # Validate API key if provided
    if api_key is not None:
        if not api_key or len(api_key.strip()) < 10:
            raise ValidationError("Invalid API key format", field="api_key", error_type="invalid_api_key")
        gemini_key.api_key = api_key.strip()
    
    if is_active is not None:
        gemini_key.is_active = is_active
    
    # Database operations
    try:
        db.add(gemini_key)
        db.commit()
        db.refresh(gemini_key)
        
        logger.info(f"Gemini API key updated successfully for user {user_id}")
        
        return GeminiKeyResponse(
            id=gemini_key.id,
            user_id=gemini_key.user_id,
            api_key_preview=_get_key_preview(gemini_key.api_key),
            is_active=gemini_key.is_active,
            created_at=gemini_key.created_at,
            updated_at=gemini_key.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error updating Gemini API key: {str(e)}", operation="update_gemini_key", error_type="transaction")

def delete_gemini_key(user_id: UUID, db: Session) -> dict:
    """Delete Gemini API key for a user"""
    gemini_key = db.exec(select(GeminiKey).where(GeminiKey.user_id == user_id)).first()
    
    if not gemini_key:
        return {
            "success": True,
            "message": "No Gemini API key found to delete"
        }
    
    # Database operations
    try:
        db.delete(gemini_key)
        db.commit()
        
        logger.info(f"Gemini API key deleted successfully for user {user_id}")
        
        return {
            "success": True,
            "message": "Gemini API key deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error deleting Gemini API key: {str(e)}", operation="delete_gemini_key", error_type="transaction")

def get_gemini_key_status(user_id: UUID, db: Session) -> GeminiKeyStatus:
    """Get Gemini API key status for a user"""
    try:
        gemini_key = db.exec(select(GeminiKey).where(GeminiKey.user_id == user_id)).first()
        
        if not gemini_key:
            return GeminiKeyStatus(
                has_key=False,
                is_active=False,
                key_preview=None
            )
        
        return GeminiKeyStatus(
            has_key=True,
            is_active=gemini_key.is_active,
            key_preview=_get_key_preview(gemini_key.api_key)
        )
        
    except Exception as e:
        raise DatabaseError(f"Error checking Gemini API key status: {str(e)}", operation="get_gemini_key_status", error_type="query")

def get_gemini_api_key_for_user(user_id: UUID, db: Session) -> Optional[str]:
    """Get the actual Gemini API key for a user (for internal use in services)"""
    try:
        gemini_key = db.exec(
            select(GeminiKey).where(
                GeminiKey.user_id == user_id,
                GeminiKey.is_active == True
            )
        ).first()
        
        return gemini_key.api_key if gemini_key else None
        
    except Exception as e:
        raise DatabaseError(f"Error getting Gemini API key: {str(e)}", operation="get_gemini_api_key_for_user", error_type="query")

def get_user_gemini_api_key(user_id: UUID, db: Session) -> Optional[str]:
    """
    Get the Gemini API key for a specific user.
    Returns None if no key is found or if the key is inactive.
    
    Args:
        user_id: The user's UUID
        db: Database session
        
    Returns:
        The user's Gemini API key or None if not found/inactive
    """
    api_key = get_gemini_api_key_for_user(user_id, db)
    
    if not api_key:
        logger.warning(f"No active Gemini API key found for user {user_id}")
        return None
        
    logger.info(f"Retrieved Gemini API key for user {user_id}")
    return api_key

def get_gemini_api_key_with_fallback(user_id: UUID, db: Session, fallback_key: str = None) -> str:
    """
    Get the user's Gemini API key with a fallback to a default key.
    
    Args:
        user_id: The user's UUID
        db: Database session
        fallback_key: Fallback API key if user doesn't have one
        
    Returns:
        The user's Gemini API key or the fallback key
    """
    user_key = get_user_gemini_api_key(user_id, db)
    
    if user_key:
        return user_key
    
    if fallback_key:
        logger.info(f"Using fallback Gemini API key for user {user_id}")
        return fallback_key
    
    # Try to get from environment as last resort
    import os
    env_key = os.getenv("GEMINI_API_KEY")
    
    if env_key:
        logger.info(f"Using environment Gemini API key for user {user_id}")
        return env_key
    
    raise GeminiKeyInvalidError("No Gemini API key available", user_id=str(user_id), error_type="invalid")

def _get_key_preview(api_key: str) -> str:
    """
    Create a preview of the API key showing first 10 and last 4 characters
    """
    if len(api_key) <= 14:
        return "*" * len(api_key)
    
    return f"{api_key[:10]}...{api_key[-4:]}" 