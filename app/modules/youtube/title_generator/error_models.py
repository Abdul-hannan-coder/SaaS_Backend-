"""
Custom error models for title generator using Pydantic and Dataclasses
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from datetime import datetime

# Error code constants for better maintainability
class ErrorCodes:
    # Title-related errors
    TITLE_GENERATION_FAILED = "TITLE_001"
    TITLE_NOT_FOUND = "TITLE_002"
    TITLE_ALREADY_EXISTS = "TITLE_003"
    TITLE_INVALID = "TITLE_004"
    TITLE_TOO_LONG = "TITLE_005"
    TITLE_TOO_SHORT = "TITLE_006"
    
    # Video-related errors
    VIDEO_NOT_FOUND = "VIDEO_001"
    VIDEO_TRANSCRIPT_NOT_FOUND = "VIDEO_002"
    VIDEO_ACCESS_DENIED = "VIDEO_003"
    
    # API-related errors
    API_KEY_MISSING = "API_001"
    API_KEY_INVALID = "API_002"
    API_QUOTA_EXCEEDED = "API_003"
    API_RATE_LIMITED = "API_004"
    
    # Database-related errors
    DATABASE_CONNECTION_FAILED = "DB_001"
    DATABASE_QUERY_FAILED = "DB_002"
    DATABASE_TRANSACTION_FAILED = "DB_003"
    DATABASE_CONSTRAINT_VIOLATION = "DB_004"
    
    # Validation-related errors
    VALIDATION_INVALID_TITLE = "VAL_001"
    VALIDATION_MISSING_REQUIRED_FIELD = "VAL_002"
    VALIDATION_FIELD_TOO_LONG = "VAL_003"
    VALIDATION_FIELD_TOO_SHORT = "VAL_004"

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
class TitleGenerationError(Exception):
    """Raised when title generation fails"""
    message: str = "Title generation failed"
    video_id: Optional[str] = None
    error_type: str = "generation_failed"  # generation_failed, api_error, quota_exceeded
    
    def __post_init__(self):
        # Map error types to specific codes
        error_code_map = {
            "generation_failed": ErrorCodes.TITLE_GENERATION_FAILED,
            "api_error": ErrorCodes.API_KEY_INVALID,
            "quota_exceeded": ErrorCodes.API_QUOTA_EXCEEDED,
            "rate_limited": ErrorCodes.API_RATE_LIMITED
        }
        
        error_code = error_code_map.get(self.error_type, ErrorCodes.TITLE_GENERATION_FAILED)
        
        details = {}
        if self.video_id:
            details["video_id"] = self.video_id
        details["error_type"] = self.error_type
            
        self.error_detail = ErrorDetail(
            message=self.message,
            code=error_code,
            details=details
        )
        super().__init__(self.error_detail.message)

@dataclass
class VideoNotFoundError(Exception):
    """Raised when video is not found"""
    message: str = "Video not found"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        details = {}
        if self.video_id:
            details["video_id"] = self.video_id
        if self.user_id:
            details["user_id"] = self.user_id
            
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ErrorCodes.VIDEO_NOT_FOUND,
            details=details if details else None
        )
        super().__init__(self.error_detail.message)

@dataclass
class VideoTranscriptNotFoundError(Exception):
    """Raised when video transcript is not found"""
    message: str = "Video transcript not found"
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        details = {}
        if self.video_id:
            details["video_id"] = self.video_id
        if self.user_id:
            details["user_id"] = self.user_id
            
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ErrorCodes.VIDEO_TRANSCRIPT_NOT_FOUND,
            details=details if details else None
        )
        super().__init__(self.error_detail.message)

@dataclass
class ApiKeyMissingError(Exception):
    """Raised when API key is missing"""
    message: str = "API key is missing"
    user_id: Optional[str] = None
    service: str = "gemini"  # gemini, openai, etc.
    
    def __post_init__(self):
        details = {}
        if self.user_id:
            details["user_id"] = self.user_id
        details["service"] = self.service
            
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ErrorCodes.API_KEY_MISSING,
            details=details
        )
        super().__init__(self.error_detail.message)

@dataclass
class ValidationError(Exception):
    """Raised when input validation fails"""
    message: str = "Validation failed"
    field: Optional[str] = None
    value: Optional[Any] = None
    error_type: str = "invalid"  # invalid_title, missing_field, too_long, too_short
    
    def __post_init__(self):
        # Map error types to specific codes
        error_code_map = {
            "invalid_title": ErrorCodes.VALIDATION_INVALID_TITLE,
            "missing_field": ErrorCodes.VALIDATION_MISSING_REQUIRED_FIELD,
            "too_long": ErrorCodes.VALIDATION_FIELD_TOO_LONG,
            "too_short": ErrorCodes.VALIDATION_FIELD_TOO_SHORT,
            "invalid": ErrorCodes.VALIDATION_INVALID_TITLE  # Default
        }
        
        error_code = error_code_map.get(self.error_type, ErrorCodes.VALIDATION_INVALID_TITLE)
        
        details = {}
        if self.field:
            details["field"] = self.field
        if self.value is not None:
            details["value"] = str(self.value)
        details["error_type"] = self.error_type
            
        self.error_detail = ErrorDetail(
            message=self.message,
            code=error_code,
            details=details
        )
        super().__init__(self.error_detail.message)

@dataclass
class DatabaseError(Exception):
    """Raised when database operation fails"""
    message: str = "Database operation failed"
    operation: Optional[str] = None
    error_type: str = "query"  # query, connection, transaction, constraint
    
    def __post_init__(self):
        # Map error types to specific codes
        error_code_map = {
            "query": ErrorCodes.DATABASE_QUERY_FAILED,
            "connection": ErrorCodes.DATABASE_CONNECTION_FAILED,
            "transaction": ErrorCodes.DATABASE_TRANSACTION_FAILED,
            "constraint": ErrorCodes.DATABASE_CONSTRAINT_VIOLATION
        }
        
        error_code = error_code_map.get(self.error_type, ErrorCodes.DATABASE_QUERY_FAILED)
        
        details = {}
        if self.operation:
            details["operation"] = self.operation
        details["error_type"] = self.error_type
            
        self.error_detail = ErrorDetail(
            message=self.message,
            code=error_code,
            details=details
        )
        super().__init__(self.error_detail.message)
