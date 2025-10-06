"""
Google OAuth routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlmodel import Session
from typing import Optional

from ....utils.database_dependency import get_database_session
from ....utils.my_logger import get_logger
from ..controllers.google_auth_controller import handle_google_callback
from ..services.google_oauth_service import get_google_authorization_url
from ..models.google_user_model import GoogleAuthResponse

logger = get_logger("GOOGLE_AUTH_ROUTES")

router = APIRouter(prefix="/auth/google", tags=["Google Authentication"])

@router.get("/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth login
    
    Redirects user to Google OAuth consent screen
    """
    try:
        # Generate state parameter for security (optional)
        state = None  # You can generate a random state for extra security
        
        # Get Google OAuth authorization URL
        auth_url = get_google_authorization_url(state=state)
        
        logger.info("Redirecting user to Google OAuth")
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error(f"Error initiating Google login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initiating Google authentication"
        )

@router.get("/callback")
async def google_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_database_session)
):
    """
    Handle Google OAuth callback
    
    This endpoint receives the authorization code from Google
    and exchanges it for user information and JWT token
    """
    try:
        # Check for OAuth errors
        if error:
            logger.warning(f"Google OAuth error: {error}")
            return HTMLResponse(
                content=f"""
                <html>
                    <body>
                        <h2>Authentication Error</h2>
                        <p>Google authentication failed: {error}</p>
                        <p><a href="/auth/google/login">Try again</a></p>
                    </body>
                </html>
                """,
                status_code=400
            )
        
        # Check for authorization code
        if not code:
            logger.warning("No authorization code received from Google")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not received"
            )
        
        # Process Google authentication
        auth_response = await handle_google_callback(code, db)
        
        # Return success page with token (in production, you might redirect to frontend)
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <title>Authentication Successful</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .container {{ max-width: 600px; margin: 0 auto; text-align: center; }}
                        .token {{ background: #f5f5f5; padding: 20px; margin: 20px 0; word-break: break-all; }}
                        .user-info {{ background: #e8f5e8; padding: 15px; margin: 20px 0; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>✅ Google Authentication Successful!</h2>
                        <div class="user-info">
                            <h3>Welcome, {auth_response.user['full_name']}!</h3>
                            <p>Email: {auth_response.user['email']}</p>
                            <p>Username: {auth_response.user['username']}</p>
                        </div>
                        <div class="token">
                            <h3>Your Access Token:</h3>
                            <p><strong>{auth_response.access_token}</strong></p>
                            <p><small>Use this token in the Authorization header: Bearer &lt;token&gt;</small></p>
                        </div>
                        <p><a href="/docs">Go to API Documentation</a></p>
                    </div>
                    <script>
                        // Store token in localStorage for frontend use
                        localStorage.setItem('access_token', '{auth_response.access_token}');
                        localStorage.setItem('user', JSON.stringify({auth_response.user}));
                    </script>
                </body>
            </html>
            """
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication processing failed"
        )

@router.get("/status")
async def google_auth_status():
    """
    Check Google OAuth configuration status
    """
    from ....config.my_settings import settings
    
    return {
        "google_oauth_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "login_url": "/auth/google/login"
    }
