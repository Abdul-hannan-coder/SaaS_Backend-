from pydantic import BaseModel
from typing import Optional

class GoogleUserInfo(BaseModel):
    """Google user information from OAuth"""
    id: str
    email: str
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    verified_email: bool = False

class GoogleTokenResponse(BaseModel):
    """Google OAuth token response"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str

class GoogleAuthResponse(BaseModel):
    """Response after successful Google authentication"""
    access_token: str
    token_type: str = "bearer"
    user: dict
