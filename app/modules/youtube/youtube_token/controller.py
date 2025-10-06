"""
Controller layer for YouTube token management
"""
from typing import Optional, Dict, Any
from uuid import UUID
from sqlmodel import Session
from pydantic import BaseModel

from .service import (
 
    get_google_token_by_user_id_service,
    is_token_expired_service,
    create_token_service,
    handle_oauth_callback_service,
    get_google_token_after_inspect_and_refresh_service,
)
from .model import GoogleToken, TokenResponse, TokenStatus, OAuthCallbackResponse, CreateTokenResponse, RefreshTokenResponse, StoredTokens
from ....utils.my_logger import get_logger

logger = get_logger("YOUTUBE_TOKEN_CONTROLLER")


class YouTubeTokenControllerResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]



def create_token_controller(user_id: UUID, db: Session) -> YouTubeTokenControllerResponse:
    """Create token - opens browser for OAuth authentication."""
    result = create_token_service(user_id, db)
    
    return YouTubeTokenControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )



def handle_oauth_callback_controller(code: str, user_id: UUID, db: Session, state: Optional[str] = None) -> YouTubeTokenControllerResponse:
    """Handle OAuth callback - exchanges authorization code for tokens and stores them."""
    result = handle_oauth_callback_service(code, user_id, db, state)
    
    return YouTubeTokenControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )




def get_google_token_by_user_id_controller(user_id: UUID, db: Session) -> YouTubeTokenControllerResponse:
    """Get Google token by user ID."""
    token = get_google_token_by_user_id_service(user_id, db)
    
    if token:
        return YouTubeTokenControllerResponse(
            success=True,
            message="Token retrieved successfully",
            data=token.dict() if hasattr(token, 'dict') else token
        )
    else:
        return YouTubeTokenControllerResponse(
            success=False,
            message="No token found for user",
            data=None
        )




def refresh_token_controller(user_id: UUID, db: Session) -> YouTubeTokenControllerResponse:
    """Refresh token - checks if token is expired and refreshes if needed."""
    try:
        tokens = get_google_token_after_inspect_and_refresh_service(user_id, db)
    
        return YouTubeTokenControllerResponse(
                success=True,
                message="Token refreshed successfully",
                data=tokens
            )
    except Exception as e:
        return YouTubeTokenControllerResponse(
            success=False,
            message=f"Failed to refresh token: {str(e)}",
            data=None
        )










