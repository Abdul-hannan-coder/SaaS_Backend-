from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, DateTime
from sqlalchemy.sql import func

class GeminiKeyBase(SQLModel):
    """Base model for Gemini API key"""
    api_key: str = Field(max_length=1000)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

class GeminiKey(GeminiKeyBase, table=True):
    """Database model for storing user Gemini API keys"""
    __tablename__ = "gemini_api_keys"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, unique=True)

class GeminiKeyCreate(SQLModel):
    """Model for creating a new Gemini API key"""
    api_key: str = Field(..., min_length=10, max_length=1000)

class GeminiKeyUpdate(SQLModel):
    """Model for updating a Gemini API key"""
    api_key: Optional[str] = Field(None, min_length=10, max_length=1000)
    is_active: Optional[bool] = None

class GeminiKeyResponse(BaseModel):
    """Model for Gemini API key response"""
    id: int
    user_id: UUID
    api_key_preview: str  # Show only first 10 and last 4 characters
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

class GeminiKeyStatus(BaseModel):
    """Model for Gemini API key status response"""
    has_key: bool
    is_active: bool
    key_preview: Optional[str] = None 