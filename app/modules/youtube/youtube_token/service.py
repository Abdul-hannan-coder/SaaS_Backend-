"""
Service layer for YouTube token management
"""
import requests
import webbrowser
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from sqlmodel import Session, select
from urllib.parse import urlencode

from .model import GoogleToken, TokenResponse, TokenStatus, OAuthCallbackResponse, CreateTokenResponse, RefreshTokenResponse, StoredTokens
from .error_models import (
    TokenCreationError,
    TokenNotFoundError,
    TokenRetrievalError,
    TokenRefreshError,
    OAuthCallbackError,
    OAuthUrlGenerationError,
    GoogleApiError,
    ValidationError,
    DatabaseError
)
from ..youtube_creds.service import get_youtube_credentials_service
from ....utils.my_logger import get_logger

logger = get_logger("YOUTUBE_TOKEN_SERVICE")

# Configuration
# REDIRECT_URI = "https://saas-backend.duckdns.org/youtube/oauth/callback"
REDIRECT_URI = "http://localhost:8000/youtube/oauth/callback"
# Google API endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# YouTube API scopes
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/bigquery.readonly",
    "https://www.googleapis.com/auth/cloud-platform.read-only",
    "https://www.googleapis.com/auth/devstorage.full_control",
    "https://www.googleapis.com/auth/devstorage.read_only",
    "https://www.googleapis.com/auth/devstorage.read_write"
]



def create_token_service(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Create token - opens browser for OAuth authentication."""
    # Generate a stronger state parameter
    state = f"user_{str(user_id)}"
    auth_url_result = _get_google_auth_url_service(user_id, db, REDIRECT_URI, state)
    
    # Open browser
    webbrowser.open(auth_url_result["auth_url"])
    
    logger.info(f"Browser opened for OAuth authentication for user {user_id}")
    
    return {
        "success": True,
        "message": "Browser opened for OAuth authentication",
        "user_id": str(user_id),
        "auth_url": auth_url_result["auth_url"],
        "instructions": "Complete authentication in browser, then check /oauth/callback for the authorization code"
    }




def handle_oauth_callback_service(code: str, user_id: UUID, db: Session, state: Optional[str] = None) -> Dict[str, Any]:
    """Handle OAuth callback - exchanges authorization code for tokens and stores them."""
    # Exchange code for tokens
    tokens_result = _exchange_code_for_tokens_service(code, user_id, db)
    
    if not tokens_result["success"]:
        raise OAuthCallbackError("Failed to exchange code for tokens", user_id=str(user_id))
    
    # Save tokens to database
    save_result = _save_tokens_to_db_service(tokens_result["tokens"], user_id, db)
    
    if not save_result["success"]:
        raise OAuthCallbackError("Failed to save tokens to database", user_id=str(user_id))
    
    logger.info(f"OAuth callback handled successfully for user {user_id}")
    
    return {
        "success": True,
        "message": "OAuth successful! Tokens saved to database.",
        "user_id": str(user_id),
        "authorization_code": code,
        "state": state,
        "tokens_saved": True,
        "access_token_preview": tokens_result["tokens"].get('access_token', '')[:20] + "..." if tokens_result["tokens"].get('access_token') else None
    }



def get_google_token_by_user_id_service(user_id: UUID, db: Session):
    """Get Google token by user ID."""
    statement = select(GoogleToken).where(GoogleToken.user_id == user_id)
    return db.exec(statement).first()



def get_google_token_after_inspect_and_refresh_service(user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Automatic token refresh function similar to calendar implementation.
    
    1. Loads tokens for user_id
    2. Checks if token is expired
    3. Automatically refreshes if expired and saves to database
    4. Returns ready-to-use tokens with user_id or None if no tokens exist
    """
    try:
        # Load current tokens from database
        tokens_result = _load_tokens_from_db_service(user_id, db)
        
        if not tokens_result["success"]:
            raise TokenNotFoundError("No Google tokens found for user", user_id=str(user_id))
        
        tokens = tokens_result["tokens"]
        
        # Check if token is expired
        if is_token_expired_service(tokens):
            logger.info(f"Google token expired for user_id: {user_id} - refreshing automatically...")
            
            # Get refresh token
            refresh_token_value = tokens.get('refresh_token')
            if not refresh_token_value:
                raise TokenRefreshError("No refresh token found for user", user_id=str(user_id))
            
            # Refresh the token
            new_tokens_result = _refresh_access_token_service(refresh_token_value, user_id, db)
            
            if not new_tokens_result["success"]:
                raise TokenRefreshError("Failed to refresh Google token for user", user_id=str(user_id))
            
            # Save new tokens to database
            save_result = _save_tokens_to_db_service(new_tokens_result["tokens"], user_id, db)
            if not save_result["success"]:
                raise TokenRefreshError("Failed to save refreshed Google tokens for user", user_id=str(user_id))
            
            logger.info(f"Successfully refreshed and saved Google tokens for user_id: {user_id}")
            # Add user_id to the returned tokens
            new_tokens_result["tokens"]['user_id'] = str(user_id)
            return new_tokens_result["tokens"]
        else:
            logger.info(f"Google token is still valid for user_id: {user_id}")
            # Add user_id to the returned tokens
            tokens['user_id'] = str(user_id)
            return tokens
            
    except Exception as e:
        if isinstance(e, (TokenNotFoundError, TokenRefreshError)):
            raise
        raise TokenRetrievalError(f"Error in token inspection and refresh: {str(e)}", user_id=str(user_id))







def _get_google_auth_url_service(user_id: UUID, db: Session, redirect_uri: str = None, state: str = "user_1") -> Dict[str, Any]:
    """Generate the Google OAuth2 authorization URL."""
    
    # Get actual credentials from database
    from sqlmodel import select
    from ..youtube_creds.model import YouTubeCredentials
    credentials = db.exec(select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)).first()
    if not credentials:
        raise ValidationError("No YouTube credentials found in database", field="credentials", error_type="missing_credentials")
    
    if redirect_uri is None:
        redirect_uri = REDIRECT_URI
    
    try:
        params = {
            "response_type": "code",
            "client_id": credentials.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(SCOPES),
            "state": state,
            "access_type": "offline",
            "prompt": "consent"  # keep refresh-token behavior
        }
        
        # Use urlencode to properly encode the parameters
        query_string = urlencode(params)
        auth_url = f"{GOOGLE_AUTH_URL}?{query_string}"
        
        logger.info(f"Successfully generated OAuth URL for user {user_id}")
        
        return {
            "success": True,
            "message": "OAuth URL generated successfully",
            "user_id": str(user_id),
            "auth_url": auth_url,
            "redirect_uri": redirect_uri,
            "state": state
        }
        
    except Exception as e:
        raise OAuthUrlGenerationError(f"Error generating OAuth URL: {str(e)}", user_id=str(user_id))


def _exchange_code_for_tokens_service(authorization_code: str, user_id: UUID, db: Session) -> Dict[str, Any]:
    """Exchange authorization code for access tokens."""
   
    # Get actual credentials from database
    from sqlmodel import select
    from ..youtube_creds.model import YouTubeCredentials
    credentials = db.exec(select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)).first()
    if not credentials:
        raise ValidationError("No YouTube credentials found in database", field="credentials", error_type="missing_credentials")
    
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "redirect_uri": REDIRECT_URI
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(GOOGLE_TOKEN_URL, data=data, headers=headers)
        logger.info(f"Google token exchange response status: {response.status_code}")
        logger.info(f"Google token exchange response: {response.text}")
        response.raise_for_status()
        
        tokens = response.json()
        logger.info(f"Successfully exchanged code for tokens for user {user_id}")
        
        return {
            "success": True,
            "message": "Code exchanged for tokens successfully",
            "user_id": str(user_id),
            "tokens": tokens
        }
        
    except requests.exceptions.RequestException as e:
        raise GoogleApiError(f"Error exchanging code for tokens: {str(e)}", api_endpoint="token_exchange", user_id=str(user_id))



def _save_tokens_to_db_service(tokens: Dict[str, Any], user_id: UUID, db: Session) -> Dict[str, Any]:
    """Save tokens to database with expiration timestamp."""
    # Database operations
    try:
        logger.info(f"Google API response tokens keys: {list(tokens.keys())}")
        # Add expiration timestamp
        if 'expires_in' in tokens:
            expires_at = datetime.now() + timedelta(seconds=tokens['expires_in'])
            tokens['expires_at'] = expires_at.isoformat()
        else:
            tokens['expires_at'] = datetime.now().isoformat()
        
        # Check if token already exists for this user
        existing_token = get_google_token_by_user_id_service(user_id, db)
        
        if existing_token:
            # Update existing token
            for key, value in tokens.items():
                if hasattr(existing_token, key):
                    setattr(existing_token, key, value)
            db.add(existing_token)
        else:
            # Create new token
            new_token = GoogleToken(
                user_id=user_id,
                access_token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_type=tokens['token_type'],
                expires_in=tokens['expires_in'],
                scope=tokens['scope'],
                expires_at=tokens['expires_at']
            )
            db.add(new_token)
        
        db.commit()
        logger.info(f"Successfully saved tokens to database for user {user_id}")
        
        return {
            "success": True,
            "message": "Tokens saved to database successfully",
            "user_id": str(user_id)
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error saving tokens to database: {str(e)}", operation="save_tokens", error_type="transaction")


def _load_tokens_from_db_service(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Load tokens from database."""
    # Database operations
    try:
        token = get_google_token_by_user_id_service(user_id, db)
        if not token:
            raise TokenNotFoundError("No tokens found for user", user_id=str(user_id))
        
        tokens_dict = {
            'access_token': token.access_token,
            'refresh_token': token.refresh_token,
            'token_type': token.token_type,
            'expires_in': token.expires_in,
            'scope': token.scope,
            'expires_at': token.expires_at,
            'refresh_token_expires_in': token.refresh_token_expires_in
        }
        
        logger.info(f"Successfully loaded tokens from database for user {user_id}")
        
        return {
            "success": True,
            "message": "Tokens loaded from database successfully",
            "user_id": str(user_id),
            "tokens": tokens_dict
        }
        
    except Exception as e:
        if isinstance(e, TokenNotFoundError):
            raise
        raise DatabaseError(f"Error loading tokens from database: {str(e)}", operation="load_tokens", error_type="query")

def is_token_expired_service(tokens: Dict[str, Any]) -> bool:
    """Check if access token is expired."""
    if 'expires_at' not in tokens:
        return True
    
    try:
        expires_at = datetime.fromisoformat(tokens['expires_at'])
        return datetime.now() >= expires_at
    except:
        return True







def _refresh_access_token_service(refresh_token: str, user_id: UUID, db: Session) -> Dict[str, Any]:
    """Refresh access token using refresh token."""
    # Get user's YouTube credentials from database
    from sqlmodel import select
    from ..youtube_creds.model import YouTubeCredentials
    credentials = db.exec(select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)).first()
    if not credentials:
        raise ValidationError("No YouTube credentials found for user", field="credentials", error_type="missing_credentials")
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(GOOGLE_TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        
        tokens = response.json()
        logger.info(f"Successfully refreshed access token for user {user_id}")
        
        return {
                "success": True,
            "message": "Access token refreshed successfully",
                "user_id": str(user_id),
            "tokens": tokens
            }
        
    except requests.exceptions.RequestException as e:
        raise GoogleApiError(f"Error refreshing token: {str(e)}", api_endpoint="token_refresh", user_id=str(user_id))
        