"""
Error models for the video module
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Structured error detail for consistent error responses"""
    message: str
    code: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper datetime serialization"""
        result = self.dict()
        result['timestamp'] = self.timestamp.isoformat()
        return result


class VideoErrorCodes:
    """Error codes for video-related operations"""
    # Video upload errors
    VIDEO_001 = "VIDEO_001"  # Invalid file type
    VIDEO_002 = "VIDEO_002"  # File upload failed
    VIDEO_003 = "VIDEO_003"  # Video not found
    VIDEO_004 = "VIDEO_004"  # Video retrieval failed
    VIDEO_005 = "VIDEO_005"  # Video update failed
    VIDEO_006 = "VIDEO_006"  # Video deletion failed
    VIDEO_007 = "VIDEO_007"  # Video processing failed
    VIDEO_008 = "VIDEO_008"  # Video download failed
    VIDEO_009 = "VIDEO_009"  # Video cleanup failed
    
    # File system errors
    FILE_001 = "FILE_001"  # File system error
    FILE_002 = "FILE_002"  # File not found
    FILE_003 = "FILE_003"  # File access denied
    
    # Validation errors
    VAL_001 = "VAL_001"  # Invalid input data
    VAL_002 = "VAL_002"  # Missing required field
    VAL_003 = "VAL_003"  # Invalid file format
    
    # Database errors
    DB_001 = "DB_001"  # Database connection error
    DB_002 = "DB_002"  # Database transaction error
    DB_003 = "DB_003"  # Database query error


@dataclass
class VideoUploadError(Exception):
    """Raised when video upload fails"""
    message: str
    user_id: Optional[str] = None
    filename: Optional[str] = None
    error_type: str = "video_upload"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.VIDEO_002,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "filename": self.filename,
                "error_type": self.error_type
            }
        )


@dataclass
class VideoNotFoundError(Exception):
    """Raised when video is not found"""
    message: str
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "video_not_found"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.VIDEO_003,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class VideoRetrievalError(Exception):
    """Raised when video retrieval fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "video_retrieval"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.VIDEO_004,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class VideoUpdateError(Exception):
    """Raised when video update fails"""
    message: str
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "video_update"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.VIDEO_005,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class VideoDeletionError(Exception):
    """Raised when video deletion fails"""
    message: str
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "video_deletion"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.VIDEO_006,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class VideoProcessingError(Exception):
    """Raised when video processing fails"""
    message: str
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "video_processing"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.VIDEO_007,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class VideoDownloadError(Exception):
    """Raised when video download fails"""
    message: str
    video_url: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "video_download"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.VIDEO_008,
            timestamp=datetime.now(),
            details={
                "video_url": self.video_url,
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class InvalidFileTypeError(Exception):
    """Raised when invalid file type is provided"""
    message: str
    file_type: Optional[str] = None
    error_type: str = "invalid_file_type"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.VIDEO_001,
            timestamp=datetime.now(),
            details={
                "file_type": self.file_type,
                "error_type": self.error_type
            }
        )


@dataclass
class FileSystemError(Exception):
    """Raised when file system operations fail"""
    message: str
    file_path: Optional[str] = None
    operation: Optional[str] = None
    error_type: str = "file_system"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.FILE_001,
            timestamp=datetime.now(),
            details={
                "file_path": self.file_path,
                "operation": self.operation,
                "error_type": self.error_type
            }
        )


@dataclass
class ValidationError(Exception):
    """Raised when input validation fails"""
    message: str
    field: Optional[str] = None
    error_type: str = "validation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.VAL_001,
            timestamp=datetime.now(),
            details={
                "field": self.field,
                "error_type": self.error_type
            }
        )


@dataclass
class DatabaseError(Exception):
    """Raised when database operations fail"""
    message: str
    operation: Optional[str] = None
    error_type: str = "database"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=VideoErrorCodes.DB_002,
            timestamp=datetime.now(),
            details={
                "operation": self.operation,
                "error_type": self.error_type
            }
        )
