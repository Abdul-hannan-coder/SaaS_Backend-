from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from uuid import UUID
from datetime import datetime

class PrivacyStatus(str, Enum):
    """Privacy status options for video uploads"""
    PRIVATE = "private"
    PUBLIC = "public"
    UNLISTED = "unlisted"

class PrivacyStatusRequest(BaseModel):
    """Request model for setting video privacy status"""
    privacy_status: PrivacyStatus = Field(..., description="Privacy status for the video")

class PrivacyStatusResponse(BaseModel):
    """Response model for privacy status"""
    success: bool
    message: str
    data: dict 