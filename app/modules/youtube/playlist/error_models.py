"""
Error models for Playlist module
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PlaylistErrorCodes:
    """Error codes for Playlist module"""
    # Playlist Operations Errors
    PLAYLIST_CREATION_FAILED = "PLAY_001"
    PLAYLIST_RETRIEVAL_FAILED = "PLAY_002"
    PLAYLIST_SELECTION_FAILED = "PLAY_003"
    PLAYLIST_VIDEOS_RETRIEVAL_FAILED = "PLAY_004"
    
    # Video Errors
    VIDEO_NOT_FOUND = "VIDEO_001"
    VIDEO_ACCESS_DENIED = "VIDEO_002"
    
    # YouTube API Errors
    YOUTUBE_API_ERROR = "YT_001"
    YOUTUBE_AUTH_ERROR = "YT_002"
    YOUTUBE_QUOTA_EXCEEDED = "YT_003"
    
    # Validation Errors
    INVALID_PLAYLIST_NAME = "VAL_001"
    PLAYLIST_NAME_TOO_LONG = "VAL_002"
    PLAYLIST_NAME_TOO_SHORT = "VAL_003"
    INVALID_PRIVACY_STATUS = "VAL_004"
    MISSING_PLAYLIST_NAME = "VAL_005"
    
    # Database Errors
    DATABASE_ERROR = "DB_001"


class ErrorDetail(BaseModel):
    """Base error detail model"""
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper datetime serialization"""
        return {
            "message": self.message,
            "code": self.code,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


@dataclass
class PlaylistCreationError(Exception):
    """Raised when playlist creation fails"""
    message: str = "Failed to create playlist"
    user_id: Optional[str] = None
    playlist_name: Optional[str] = None
    error_type: str = "creation_failed"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PlaylistErrorCodes.PLAYLIST_CREATION_FAILED,
            details={
                "user_id": self.user_id,
                "playlist_name": self.playlist_name,
                "error_type": self.error_type
            } if self.user_id or self.playlist_name else {"error_type": self.error_type}
        )
        super().__init__(self.error_detail.message)


@dataclass
class PlaylistRetrievalError(Exception):
    """Raised when playlist retrieval fails"""
    message: str = "Failed to retrieve playlists"
    user_id: Optional[str] = None
    error_type: str = "retrieval_failed"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PlaylistErrorCodes.PLAYLIST_RETRIEVAL_FAILED,
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            } if self.user_id else {"error_type": self.error_type}
        )
        super().__init__(self.error_detail.message)


@dataclass
class PlaylistSelectionError(Exception):
    """Raised when playlist selection fails"""
    message: str = "Failed to select playlist"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    playlist_name: Optional[str] = None
    error_type: str = "selection_failed"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PlaylistErrorCodes.PLAYLIST_SELECTION_FAILED,
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "playlist_name": self.playlist_name,
                "error_type": self.error_type
            } if self.video_id or self.user_id or self.playlist_name else {"error_type": self.error_type}
        )
        super().__init__(self.error_detail.message)


@dataclass
class VideoNotFoundError(Exception):
    """Raised when a video is not found"""
    message: str = "Video not found"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PlaylistErrorCodes.VIDEO_NOT_FOUND,
            details={"video_id": self.video_id, "user_id": self.user_id} if self.video_id or self.user_id else None
        )
        super().__init__(self.error_detail.message)


@dataclass
class VideoAccessDeniedError(Exception):
    """Raised when user doesn't have access to the video"""
    message: str = "Access denied to video"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PlaylistErrorCodes.VIDEO_ACCESS_DENIED,
            details={"video_id": self.video_id, "user_id": self.user_id} if self.video_id or self.user_id else None
        )
        super().__init__(self.error_detail.message)


@dataclass
class YouTubeApiError(Exception):
    """Raised when YouTube API operations fail"""
    message: str = "YouTube API error"
    error_type: str = "api_error"
    api_error_code: Optional[str] = None
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PlaylistErrorCodes.YOUTUBE_API_ERROR,
            details={
                "error_type": self.error_type,
                "api_error_code": self.api_error_code
            } if self.api_error_code else {"error_type": self.error_type}
        )
        super().__init__(self.error_detail.message)


@dataclass
class YouTubeAuthError(Exception):
    """Raised when YouTube authentication fails"""
    message: str = "YouTube authentication failed"
    user_id: Optional[str] = None
    error_type: str = "auth_failed"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PlaylistErrorCodes.YOUTUBE_AUTH_ERROR,
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            } if self.user_id else {"error_type": self.error_type}
        )
        super().__init__(self.error_detail.message)


@dataclass
class ValidationError(Exception):
    """Raised when validation fails"""
    message: str = "Validation error"
    field: Optional[str] = None
    error_type: str = "validation_failed"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PlaylistErrorCodes.INVALID_PLAYLIST_NAME,
            details={"field": self.field, "error_type": self.error_type} if self.field or self.error_type != "validation_failed" else None
        )
        super().__init__(self.error_detail.message)


@dataclass
class DatabaseError(Exception):
    """Raised when database operation fails"""
    message: str = "Database operation failed"
    operation: Optional[str] = None
    error_type: str = "database_error"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PlaylistErrorCodes.DATABASE_ERROR,
            details={"operation": self.operation, "error_type": self.error_type} if self.operation or self.error_type != "database_error" else None
        )
        super().__init__(self.error_detail.message)
