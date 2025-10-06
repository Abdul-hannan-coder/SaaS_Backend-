"""
Controller layer for YouTube credentials management
"""
from sqlmodel import Session
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel

from .service import (
    create_youtube_credentials_service,
    get_youtube_credentials_service,
    update_youtube_credentials_service,
    delete_youtube_credentials_service,
    get_youtube_credentials_status_service
)
from .model import (
    YouTubeCredentialsCreate,
    YouTubeCredentialsUpdate,
    YouTubeCredentialsResponse,
    YouTubeCredentialsStatus
)
from ....utils.my_logger import get_logger

logger = get_logger("YOUTUBE_CREDENTIALS_CONTROLLER")


class YouTubeCredentialsControllerResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]


def create_youtube_credentials_controller(
    user_id: UUID,
    client_id: str,
    client_secret: str,
    db: Session
) -> YouTubeCredentialsControllerResponse:
    """Create YouTube credentials for a user"""
    result = create_youtube_credentials_service(user_id, client_id, client_secret, db)
    
    return YouTubeCredentialsControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )


def get_youtube_credentials_controller(
    user_id: UUID,
    db: Session
) -> YouTubeCredentialsControllerResponse:
    """Get YouTube credentials for a user"""
    result = get_youtube_credentials_service(user_id, db)
    
    return YouTubeCredentialsControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )


def update_youtube_credentials_controller(
    user_id: UUID,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = None
) -> YouTubeCredentialsControllerResponse:
    """Update YouTube credentials for a user"""
    result = update_youtube_credentials_service(user_id, client_id, client_secret, is_active, db)
    
    return YouTubeCredentialsControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )


def delete_youtube_credentials_controller(
    user_id: UUID,
    db: Session
) -> YouTubeCredentialsControllerResponse:
    """Delete YouTube credentials for a user"""
    result = delete_youtube_credentials_service(user_id, db)
    
    return YouTubeCredentialsControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )


def get_youtube_credentials_status_controller(
    user_id: UUID,
    db: Session
) -> YouTubeCredentialsControllerResponse:
    """Get YouTube credentials status for a user"""
    result = get_youtube_credentials_status_service(user_id, db)
    
    return YouTubeCredentialsControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )