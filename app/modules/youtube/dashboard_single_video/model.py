from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import LONGTEXT
from uuid import UUID

class SingleVideoDetails(SQLModel, table=True):
    """Model for single video details - database table"""
    __tablename__ = "single_video_details"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: str = Field(max_length=50, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    thumbnail_link: Optional[str] = Field(default=None, max_length=1000)
    playlist: Optional[str] = Field(default=None, max_length=200)
    playlist_name: Optional[str] = Field(default=None, max_length=500)
    privacy_status: Optional[str] = Field(default=None, max_length=20)
    transcript: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    custom_thumbnail_path: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    
    # YouTube Analytics Fields
    view_count: Optional[int] = Field(default=None)
    like_count: Optional[int] = Field(default=None) 
    comment_count: Optional[int] = Field(default=None)
    watch_time_minutes: Optional[float] = Field(default=None)  # Average watch time in minutes
    published_at: Optional[datetime] = Field(default=None)
    youtube_video_url: Optional[str] = Field(default=None, max_length=500)
    days_since_published: Optional[int] = Field(default=None)
    views_per_day: Optional[float] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Add unique constraint for user_id + video_id combination
    __table_args__ = (
        {"extend_existing": True}
    )


class SingleVideoDetailsResponse(SQLModel):
    """Response model for single video details"""
    video_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_link: Optional[str] = None
    playlist: Optional[str] = None
    playlist_name: Optional[str] = None
    privacy_status: Optional[str] = None
    transcript: Optional[str] = None
    custom_thumbnail_path: Optional[str] = None
    
    # YouTube Analytics Fields
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    watch_time_minutes: Optional[float] = None
    published_at: Optional[datetime] = None
    youtube_video_url: Optional[str] = None
    days_since_published: Optional[int] = None
    views_per_day: Optional[float] = None
    
    transcript_available: bool = False
    transcript_source: Optional[str] = None  # "database" or "youtube" or None


class SingleVideoResponse(SQLModel):
    """Response model for single video details"""
    success: bool
    message: str
    video_details: SingleVideoDetails
    refreshed: bool = False  # Indicates if data was refreshed from YouTube


class UpdateVideoRequest(SQLModel):
    """Request model for updating video details"""
    title: Optional[str] = None
    description: Optional[str] = None
    privacy_status: Optional[str] = None  # public, private, unlisted
    playlist_id: Optional[str] = None  # playlist ID to add video to, or null to remove from current playlist


class UpdateVideoResponse(SQLModel):
    """Response model for video update"""
    success: bool
    message: str
    updated_fields: list[str]
    video_details: Optional[SingleVideoDetailsResponse] = None


class DeleteVideoResponse(SQLModel):
    """Response model for video deletion"""
    success: bool
    message: str
    deleted_video_id: Optional[str] = None


class ThumbnailUpdateResponse(SQLModel):
    """Response model for thumbnail update"""
    success: bool
    message: str
    video_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    method_used: Optional[str] = None
