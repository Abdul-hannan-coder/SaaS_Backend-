from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from fastapi.responses import HTMLResponse
from typing import Optional
from uuid import UUID
import os
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/views")

from .model import GoogleToken, TokenStatus, CreateTokenResponse, RefreshTokenResponse
from .controller import (
    create_token_controller,
    handle_oauth_callback_controller,
    get_google_token_by_user_id_controller,
    refresh_token_controller,
    YouTubeTokenControllerResponse
)
from ....modules.login_logout.models.user_model import UserSignUp
from ..helpers.auth_utils import get_current_user_from_token
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user

router = APIRouter(prefix="/youtube", tags=["Youtube Token"])

@router.post("/create-token", response_model=YouTubeTokenControllerResponse)
async def create_oauth_token(
    db: Session = Depends(get_database_session),
    current_user: UserSignUp = Depends(get_current_user)
):
    """
    Create OAuth token - opens browser for Google authentication.
    """
    return create_token_controller(current_user.id, db)



@router.get("/oauth/callback", response_class=HTMLResponse)
async def oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: Session = Depends(get_database_session)
):
    """Route 2: OAuth callback - exchanges authorization code for tokens and stores them."""
    if error:
        return templates.TemplateResponse('error.html', {
            'request': {},
            'error': error, 
            'error_description': error_description or "Unknown error"
        })
    
    if not code:
        return templates.TemplateResponse('error.html', {
            'request': {},
            'error': "No authorization code received", 
            'error_description': "The OAuth process did not return an authorization code"
        })
    
    try:
        # Extract user_id from state parameter
        if state and state.startswith("user_"):
            try:
                user_id = UUID(state.split("_")[1])
            except ValueError:
                return templates.TemplateResponse('error.html', {
                    'request': {},
                    'error': "Invalid user ID format", 
                    'error_description': "The user ID in the state parameter is not a valid UUID"
                })
        else:
            return templates.TemplateResponse('error.html', {
                'request': {},
                'error': "Invalid state parameter", 
                'error_description': "The OAuth state parameter is missing or invalid"
            })
        
        # Handle OAuth callback and save tokens
        handle_oauth_callback_controller(code, user_id, db, state)
        
        # Return success HTML page from template
        return templates.TemplateResponse('oauth_success.html', {
            'request': {},
            'service_name': 'Google Calendar',
            'service_logo': '/static/calendar-logo.png'
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get user token 
@router.get("/get-token", response_model=YouTubeTokenControllerResponse)
async def get_token(
    db: Session = Depends(get_database_session),
    current_user: UserSignUp = Depends(get_current_user)
):
    """
    Get user token.
    """
    return get_google_token_by_user_id_controller(current_user.id, db)



@router.post("/refresh-token", response_model=YouTubeTokenControllerResponse)
async def refresh_oauth_token(
    db: Session = Depends(get_database_session),
    current_user: UserSignUp = Depends(get_current_user)
):
    """
    Manually refresh OAuth token for the current user.
    """
    return refresh_token_controller(current_user.id, db)



