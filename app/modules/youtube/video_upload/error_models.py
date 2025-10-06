"""
Error models for video upload module
"""
from dataclasses import dataclass
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class ErrorDetail(BaseModel):
    """Structured error detail for consistent error responses"""
    message: str
    code: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper datetime serialization"""
        return {
            "message": self.message,
            "code": self.code,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


class VideoUploadErrorCodes:
    """Error codes for video upload operations"""
    # Upload errors
    UPLOAD_001 = "UPLOAD_001"  # Video upload failed
    UPLOAD_002 = "UPLOAD_002"  # Video file not found
    UPLOAD_003 = "UPLOAD_003"  # Invalid video format
    UPLOAD_004 = "UPLOAD_004"  # Upload interrupted
    UPLOAD_005 = "UPLOAD_005"  # Thumbnail upload failed
    UPLOAD_006 = "UPLOAD_006"  # Playlist addition failed
    UPLOAD_007 = "UPLOAD_007"  # Video metadata invalid
    UPLOAD_008 = "UPLOAD_008"  # YouTube API quota exceeded
    UPLOAD_009 = "UPLOAD_009"  # Video too large
    UPLOAD_010 = "UPLOAD_010"  # Upload timeout
    
    # YouTube API errors
    API_001 = "API_001"  # YouTube API connection failed
    API_002 = "API_002"  # YouTube API authentication failed
    API_003 = "API_003"  # YouTube API quota exceeded
    API_004 = "API_004"  # YouTube API rate limit exceeded
    API_005 = "API_005"  # YouTube API invalid request
    API_006 = "API_006"  # YouTube API service unavailable
    
    # Validation errors
    VAL_001 = "VAL_001"  # Invalid video ID
    VAL_002 = "VAL_002"  # Invalid user ID
    VAL_003 = "VAL_003"  # Missing video metadata
    VAL_004 = "VAL_004"  # Invalid privacy status
    VAL_005 = "VAL_005"  # Invalid schedule datetime
    VAL_006 = "VAL_006"  # Invalid playlist name
    
    # Database errors
    DB_001 = "DB_001"  # Database connection failed
    DB_002 = "DB_002"  # Video not found in database
    DB_003 = "DB_003"  # Database update failed
    DB_004 = "DB_004"  # Database transaction failed


@dataclass
class VideoUploadError(Exception):
    """Exception raised when video upload fails"""
    message: str
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "upload_failure"
    operation: str = "video_upload"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_001,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class VideoFileNotFoundError(Exception):
    """Exception raised when video file is not found"""
    message: str
    video_id: Optional[str] = None
    file_path: Optional[str] = None
    error_type: str = "file_not_found"
    operation: str = "file_validation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_002,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "file_path": self.file_path,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class InvalidVideoFormatError(Exception):
    """Exception raised when video format is invalid"""
    message: str
    video_id: Optional[str] = None
    file_format: Optional[str] = None
    error_type: str = "invalid_format"
    operation: str = "format_validation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_003,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "file_format": self.file_format,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class UploadInterruptedError(Exception):
    """Exception raised when upload is interrupted"""
    message: str
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    progress: Optional[int] = None
    error_type: str = "upload_interrupted"
    operation: str = "video_upload"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_004,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "progress": self.progress,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class ThumbnailUploadError(Exception):
    """Exception raised when thumbnail upload fails"""
    message: str
    video_id: Optional[str] = None
    youtube_video_id: Optional[str] = None
    thumbnail_path: Optional[str] = None
    error_type: str = "thumbnail_upload_failure"
    operation: str = "thumbnail_upload"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_005,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "youtube_video_id": self.youtube_video_id,
                "thumbnail_path": self.thumbnail_path,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class PlaylistAdditionError(Exception):
    """Exception raised when adding video to playlist fails"""
    message: str
    video_id: Optional[str] = None
    youtube_video_id: Optional[str] = None
    playlist_name: Optional[str] = None
    error_type: str = "playlist_addition_failure"
    operation: str = "playlist_addition"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_006,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "youtube_video_id": self.youtube_video_id,
                "playlist_name": self.playlist_name,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class VideoMetadataError(Exception):
    """Exception raised when video metadata is invalid"""
    message: str
    video_id: Optional[str] = None
    field: Optional[str] = None
    error_type: str = "metadata_invalid"
    operation: str = "metadata_validation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_007,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "field": self.field,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class YouTubeApiQuotaError(Exception):
    """Exception raised when YouTube API quota is exceeded"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "quota_exceeded"
    operation: str = "api_call"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_008,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class VideoTooLargeError(Exception):
    """Exception raised when video file is too large"""
    message: str
    video_id: Optional[str] = None
    file_size: Optional[int] = None
    max_size: Optional[int] = None
    error_type: str = "file_too_large"
    operation: str = "size_validation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_009,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "file_size": self.file_size,
                "max_size": self.max_size,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class UploadTimeoutError(Exception):
    """Exception raised when upload times out"""
    message: str
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    timeout_duration: Optional[int] = None
    error_type: str = "upload_timeout"
    operation: str = "video_upload"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.UPLOAD_010,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "timeout_duration": self.timeout_duration,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class YouTubeApiError(Exception):
    """Exception raised for YouTube API errors"""
    message: str
    api_endpoint: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "api_error"
    operation: str = "api_call"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.API_001,
            timestamp=datetime.now(),
            details={
                "api_endpoint": self.api_endpoint,
                "user_id": self.user_id,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class ValidationError(Exception):
    """Exception raised for validation errors"""
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None
    error_type: str = "validation_error"
    operation: str = "validation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.VAL_001,
            timestamp=datetime.now(),
            details={
                "field": self.field,
                "value": self.value,
                "error_type": self.error_type,
                "operation": self.operation
            }
        )


@dataclass
class DatabaseError(Exception):
    """Exception raised for database errors"""
    message: str
    operation: Optional[str] = None
    error_type: str = "database_error"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoUploadErrorCodes.DB_001,
            timestamp=datetime.now(),
            details={
                "operation": self.operation,
                "error_type": self.error_type
            }
        )



