"""
Error models for Timestamps Generator module
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TimestampsErrorCodes:
    """Error codes for Timestamps Generator module"""
    # Timestamps Generation Errors
    TIMESTAMPS_GENERATION_FAILED = "TIME_001"
    TIMESTAMPS_SAVE_FAILED = "TIME_002"
    TIMESTAMPS_REGENERATION_FAILED = "TIME_003"
    
    # Video Errors
    VIDEO_NOT_FOUND = "VIDEO_001"
    VIDEO_TRANSCRIPT_NOT_FOUND = "VIDEO_002"
    
    # API Key Errors
    API_KEY_MISSING = "API_001"
    API_KEY_INVALID = "API_002"
    
    # Validation Errors
    INVALID_TIMESTAMPS = "VAL_001"
    TIMESTAMPS_TOO_LONG = "VAL_002"
    TIMESTAMPS_TOO_SHORT = "VAL_003"
    INVALID_TIMESTAMP_FORMAT = "VAL_004"
    
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
class TimestampsGenerationError(Exception):
    """Raised when timestamps generation fails"""
    message: str = "Timestamps generation failed"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "generation_failed"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=TimestampsErrorCodes.TIMESTAMPS_GENERATION_FAILED,
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "error_type": self.error_type
            } if self.video_id or self.user_id else {"error_type": self.error_type}
        )
        super().__init__(self.error_detail.message)


@dataclass
class TimestampsSaveError(Exception):
    """Raised when timestamps save fails"""
    message: str = "Failed to save timestamps"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "save_failed"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=TimestampsErrorCodes.TIMESTAMPS_SAVE_FAILED,
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "error_type": self.error_type
            } if self.video_id or self.user_id else {"error_type": self.error_type}
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
            code=TimestampsErrorCodes.VIDEO_NOT_FOUND,
            details={"video_id": self.video_id, "user_id": self.user_id} if self.video_id or self.user_id else None
        )
        super().__init__(self.error_detail.message)


@dataclass
class VideoTranscriptNotFoundError(Exception):
    """Raised when video transcript is not found"""
    message: str = "Video transcript not found"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=TimestampsErrorCodes.VIDEO_TRANSCRIPT_NOT_FOUND,
            details={"video_id": self.video_id, "user_id": self.user_id} if self.video_id or self.user_id else None
        )
        super().__init__(self.error_detail.message)


@dataclass
class ApiKeyMissingError(Exception):
    """Raised when API key is missing"""
    message: str = "API key is required for timestamps generation"
    user_id: Optional[str] = None
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=TimestampsErrorCodes.API_KEY_MISSING,
            details={"user_id": self.user_id} if self.user_id else None
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
            code=TimestampsErrorCodes.INVALID_TIMESTAMPS,
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
            code=TimestampsErrorCodes.DATABASE_ERROR,
            details={"operation": self.operation, "error_type": self.error_type} if self.operation or self.error_type != "database_error" else None
        )
        super().__init__(self.error_detail.message)
