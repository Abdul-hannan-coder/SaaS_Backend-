"""
Google OAuth service functions for handling authentication
"""
import httpx
from fastapi import HTTPException, status
from typing import Optional
from ....config.my_settings import settings
from ....utils.my_logger import get_logger
from ..models.google_user_model import GoogleUserInfo, GoogleTokenResponse

logger = get_logger("GOOGLE_OAUTH")

# OAuth configuration
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_SCOPES = ["openid", "email", "profile"]

def get_google_authorization_url(state: Optional[str] = None) -> str:
    """Generate Google OAuth authorization URL"""
    try:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": " ".join(GOOGLE_SCOPES),
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{GOOGLE_AUTH_URL}?{query_string}"
        
        logger.info("Generated Google OAuth authorization URL")
        return auth_url
        
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating authorization URL"
        )

async def exchange_code_for_token(code: str) -> GoogleTokenResponse:
    """Exchange authorization code for access token"""
    try:
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(GOOGLE_TOKEN_URL, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully exchanged code for token")
            return GoogleTokenResponse(**token_data)
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during token exchange: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization code"
        )
    except Exception as e:
        logger.error(f"Error exchanging code for token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during token exchange"
        )

async def get_google_user_info(access_token: str) -> GoogleUserInfo:
    """Get user information from Google using access token"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(GOOGLE_USERINFO_URL, headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            logger.info(f"Retrieved user info for: {user_data.get('email', 'unknown')}")
            return GoogleUserInfo(**user_data)
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )
