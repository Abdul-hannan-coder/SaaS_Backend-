from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class UserPlaylist(SQLModel, table=True):
    """Database model for storing user playlist data with analytics"""
    
    __tablename__ = "user_playlist"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    playlist_id: str = Field(max_length=200, index=True)
    playlist_name: str = Field(max_length=500)
    
    # Analytics fields
    total_views: Optional[int] = Field(default=0)
    total_likes: Optional[int] = Field(default=0)
    total_comments: Optional[int] = Field(default=0)
    average_engagement_rate: Optional[float] = Field(default=0.0)
    top_video_by_views_id: Optional[str] = Field(default=None, max_length=200)
    top_video_by_likes_id: Optional[str] = Field(default=None, max_length=200)
    top_video_by_views_title: Optional[str] = Field(default=None, max_length=500)
    top_video_by_likes_title: Optional[str] = Field(default=None, max_length=500)
    top_video_by_views_count: Optional[int] = Field(default=0)
    top_video_by_likes_count: Optional[int] = Field(default=0)
    last_analytics_update: Optional[datetime] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Add unique constraint for user_id + playlist_id combination
    __table_args__ = (
        {"extend_existing": True}
    )


class PlaylistResponse(SQLModel):
    """Response model for playlist data"""
    playlist_id: str
    playlist_name: str


class PlaylistControllerResponse(SQLModel):
    """Controller response model for playlists"""
    success: bool
    message: str
    data: Dict[str, Any]
    refreshed: bool = False


class PlaylistAnalytics(SQLModel):
    """Analytics data for playlist"""
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    average_engagement_rate: float = 0.0
    top_video_by_views_id: Optional[str] = None
    top_video_by_likes_id: Optional[str] = None
    top_video_by_views_title: Optional[str] = None
    top_video_by_likes_title: Optional[str] = None
    top_video_by_views_count: int = 0
    top_video_by_likes_count: int = 0
    last_analytics_update: Optional[str] = None


class PlaylistDetailsResponse(SQLModel):
    """Response model for detailed playlist information"""
    playlist_id: str
    playlist_name: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_count: int = 0
    published_at: Optional[str] = None
    channel_title: Optional[str] = None
    privacy_status: Optional[str] = None
    top_videos: Optional[List[Dict[str, Any]]] = None
    analytics: Optional[PlaylistAnalytics] = None


class PlaylistDetailsControllerResponse(SQLModel):
    """Controller response model for single playlist details"""
    success: bool
    message: str
    data: Optional[PlaylistDetailsResponse] = None


class PlaylistAllVideosResponse(SQLModel):
    """Response model for all videos in a playlist"""
    playlist_id: str
    playlist_name: str
    total_videos: int
    videos: List[Dict[str, Any]]


class PlaylistAllVideosControllerResponse(SQLModel):
    """Controller response model for all playlist videos"""
    success: bool
    message: str
    data: Optional[PlaylistAllVideosResponse] = None
