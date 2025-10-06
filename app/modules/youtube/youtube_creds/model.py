from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, DateTime
from sqlalchemy.sql import func

class YouTubeCredentialsBase(SQLModel):
    """Base model for YouTube credentials"""
    client_id: str = Field(max_length=200)
    client_secret: str = Field(max_length=200)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

class YouTubeCredentials(YouTubeCredentialsBase, table=True):
    """Database model for storing user YouTube credentials"""
    __tablename__ = "youtube_credentials"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, unique=True)

class YouTubeCredentialsCreate(SQLModel):
    """Model for creating new YouTube credentials"""
    client_id: str = Field(..., min_length=10, max_length=200)
    client_secret: str = Field(..., min_length=10, max_length=200)

class YouTubeCredentialsUpdate(SQLModel):
    """Model for updating YouTube credentials"""
    client_id: Optional[str] = Field(None, min_length=10, max_length=200)
    client_secret: Optional[str] = Field(None, min_length=10, max_length=200)
    is_active: Optional[bool] = None

class YouTubeCredentialsResponse(BaseModel):
    """Model for YouTube credentials response"""
    id: int
    user_id: UUID
    client_id_preview: str  # Show only first 10 and last 4 characters
    client_secret_preview: str  # Show only first 10 and last 4 characters
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

class YouTubeCredentialsStatus(BaseModel):
    """Model for YouTube credentials status response"""
    has_credentials: bool
    is_active: bool
    client_id_preview: Optional[str] = None
    client_secret_preview: Optional[str] = None
