from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, DateTime
from sqlalchemy.sql import func

class TokenResponse(BaseModel):
    """Model for token exchange response"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    scope: str

class TokenStatus(BaseModel):
    """Model for token status response"""
    status: str  # "valid", "expired", "no_tokens"
    message: str
    has_access_token: bool
    has_refresh_token: bool
    expires_at: Optional[str]
    token_type: Optional[str]
    scope: Optional[str]
    access_token_preview: Optional[str]

class OAuthCallbackResponse(BaseModel):
    """Model for OAuth callback response"""
    success: bool
    message: str
    authorization_code: str
    state: Optional[str]
    tokens_saved: bool
    access_token_preview: Optional[str]

class CreateTokenResponse(BaseModel):
    """Model for create token response"""
    message: str
    auth_url: str
    instructions: str

class RefreshTokenResponse(BaseModel):
    """Model for refresh token response"""
    success: Optional[bool]
    message: str
    expires_at: Optional[str]
    token_preview: Optional[str]
    new_token_preview: Optional[str]

class StoredTokens(BaseModel):
    """Model for tokens stored in JSON file"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    scope: str
    expires_at: str

class GoogleToken(SQLModel, table=True):
    """Database model for storing Google OAuth tokens"""
    __tablename__ = "youtube_oauth_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, unique=True)
    access_token: str = Field(max_length=2000)
    refresh_token: str = Field(max_length=2000)
    token_type: str = Field(max_length=50)
    expires_in: int
    scope: str = Field(max_length=2000)
    expires_at: str = Field(max_length=100)
    refresh_token_expires_in: Optional[int] = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

class AccessTokenResponse(BaseModel):
    """Model for access token response"""
    access_token: str 