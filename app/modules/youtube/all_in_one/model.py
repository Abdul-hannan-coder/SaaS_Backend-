"""
All-in-one video processing models
"""
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field
from uuid import UUID


class AllInOneRequest(SQLModel):
    """Request model for all-in-one video processing"""
    video_id: Optional[str] = Field(default=None, description="Video ID (set internally from path parameter)")


class TitleResult(SQLModel):
    """Result model for title generation"""
    success: bool
    message: str
    generated_titles: List[str]
    error: Optional[str] = None


class DescriptionResult(SQLModel):
    """Result model for description generation"""
    success: bool
    message: str
    generated_description: Optional[str] = None
    error: Optional[str] = None


class TimestampsResult(SQLModel):
    """Result model for timestamps generation"""
    success: bool
    message: str
    generated_timestamps: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class ThumbnailsResult(SQLModel):
    """Result model for thumbnails generation"""
    success: bool
    message: str
    generated_thumbnails: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class AllInOneResponse(SQLModel):
    """Response model for all-in-one video processing"""
    success: bool
    message: str
    video_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    results: Dict[str, Any] = Field(description="Results for each generation task")
    processing_time_seconds: float
    errors: List[str] = Field(default_factory=list, description="List of any errors encountered")


class SaveContentRequest(SQLModel):
    """Request model for saving generated content"""
    selected_title: Optional[str] = Field(default=None, description="Selected title to save")
    selected_thumbnail_url: Optional[str] = Field(default=None, description="Selected thumbnail URL to download and save")
    description: Optional[str] = Field(default=None, description="Generated description to save")
    timestamps: Optional[List[Dict[str, Any]]] = Field(default=None, description="Generated timestamps to save")
    privacy_status: Optional[str] = Field(default=None, description="Privacy status for the video (public, private, unlisted)")
    playlist_name: Optional[str] = Field(default=None, description="Playlist name for the video")
    schedule_datetime: Optional[str] = Field(default=None, description="Schedule datetime for the video (ISO format)")


class SaveContentResponse(SQLModel):
    """Response model for saving generated content"""
    success: bool
    message: str
    video_id: str
    saved_content: Dict[str, Any]
    thumbnail_path: Optional[str] = None
