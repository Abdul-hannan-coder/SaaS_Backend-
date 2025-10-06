"""
Main Google OAuth module - functional approach
All Google OAuth functionality in one place
"""
from .services.google_oauth_service import (
    get_google_authorization_url,
    exchange_code_for_token,
    get_google_user_info
)
from .controllers.google_auth_controller import (
    handle_google_callback,
    find_or_create_user,
    generate_username_from_email
)
from .models.google_user_model import (
    GoogleUserInfo,
    GoogleTokenResponse,
    GoogleAuthResponse
)

# Re-export all functions for easy import
__all__ = [
    # Service functions
    "get_google_authorization_url",
    "exchange_code_for_token", 
    "get_google_user_info",
    
    # Controller functions
    "handle_google_callback",
    "find_or_create_user",
    "generate_username_from_email",
    
    # Models
    "GoogleUserInfo",
    "GoogleTokenResponse", 
    "GoogleAuthResponse"
]
