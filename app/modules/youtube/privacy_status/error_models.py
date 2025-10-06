"""
Error models for Privacy Status module
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PrivacyStatusErrorCodes:
    """Error codes for Privacy Status module"""
    # Privacy Status Errors
    PRIVACY_STATUS_UPDATE_FAILED = "PRIV_001"
    PRIVACY_STATUS_GET_FAILED = "PRIV_002"
    
    # Video Errors
    VIDEO_NOT_FOUND = "VIDEO_001"
    VIDEO_ACCESS_DENIED = "VIDEO_002"
    
    # Validation Errors
    INVALID_PRIVACY_STATUS = "VAL_001"
    MISSING_PRIVACY_STATUS = "VAL_002"
    
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
class PrivacyStatusUpdateError(Exception):
    """Raised when privacy status update fails"""
    message: str = "Failed to update privacy status"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "update_failed"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PrivacyStatusErrorCodes.PRIVACY_STATUS_UPDATE_FAILED,
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "error_type": self.error_type
            } if self.video_id or self.user_id else {"error_type": self.error_type}
        )
        super().__init__(self.error_detail.message)


@dataclass
class PrivacyStatusGetError(Exception):
    """Raised when privacy status retrieval fails"""
    message: str = "Failed to get privacy status"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "get_failed"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=PrivacyStatusErrorCodes.PRIVACY_STATUS_GET_FAILED,
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
            code=PrivacyStatusErrorCodes.VIDEO_NOT_FOUND,
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
            code=PrivacyStatusErrorCodes.VIDEO_ACCESS_DENIED,
            details={"video_id": self.video_id, "user_id": self.user_id} if self.video_id or self.user_id else None
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
            code=PrivacyStatusErrorCodes.INVALID_PRIVACY_STATUS,
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
            code=PrivacyStatusErrorCodes.DATABASE_ERROR,
            details={"operation": self.operation, "error_type": self.error_type} if self.operation or self.error_type != "database_error" else None
        )
        super().__init__(self.error_detail.message)
