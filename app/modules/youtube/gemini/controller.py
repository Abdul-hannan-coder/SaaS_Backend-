"""
Gemini API key controller - handles HTTP concerns and maps service exceptions to HTTP responses
"""
from typing import Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException, status
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
from .service import (
    create_gemini_key,
    get_gemini_key,
    update_gemini_key,
    delete_gemini_key,
    get_gemini_key_status,
    get_gemini_api_key_for_user
)
from ....utils.my_logger import get_logger

logger = get_logger("GEMINI_KEY_CONTROLLER")

def create_gemini_key_controller(
    user_id: UUID,
    api_key: str,
    db: Session
) -> GeminiKeyResponse:
    """Create a new Gemini API key for a user - HTTP layer only"""
    return create_gemini_key(user_id, api_key, db)

def get_gemini_key_controller(
    user_id: UUID,
    db: Session
) -> Optional[GeminiKeyResponse]:
    """Get Gemini API key for a user - HTTP layer only"""
    return get_gemini_key(user_id, db)

def update_gemini_key_controller(
    user_id: UUID,
    api_key: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = None
) -> Optional[GeminiKeyResponse]:
    """Update Gemini API key for a user - HTTP layer only"""
    return update_gemini_key(user_id, api_key, is_active, db)

def delete_gemini_key_controller(
    user_id: UUID,
    db: Session
) -> dict:
    """Delete Gemini API key for a user - HTTP layer only"""
    return delete_gemini_key(user_id, db)

def get_gemini_key_status_controller(
    user_id: UUID,
    db: Session
) -> GeminiKeyStatus:
    """Get Gemini API key status for a user - HTTP layer only"""
    return get_gemini_key_status(user_id, db) 