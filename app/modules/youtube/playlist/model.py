from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class PrivacyStatus(str, Enum):
    """Privacy status options for playlists"""
    PRIVATE = "private"
    PUBLIC = "public"
    UNLISTED = "unlisted"

class PlaylistCreateRequest(BaseModel):
    """Request model for creating a new playlist"""
    playlist_name: str = Field(..., description="Name of the playlist", min_length=1, max_length=150)
    description: Optional[str] = Field(default="", description="Description of the playlist", max_length=5000)
    privacy_status: Optional[PrivacyStatus] = Field(default=PrivacyStatus.PRIVATE, description="Privacy status of the playlist")

class PlaylistResponse(BaseModel):
    """Response model for playlist data"""
    id: str
    title: str
    description: str
    privacy: str

class PlaylistCreateResponse(BaseModel):
    """Response model for playlist creation"""
    playlist_id: str
    playlist_name: str
    description: str
    status: str 