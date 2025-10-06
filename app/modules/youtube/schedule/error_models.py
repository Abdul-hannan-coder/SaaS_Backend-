"""
Error models for the schedule module
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


class ScheduleErrorCodes:
    """Error codes for schedule-related operations"""
    # Schedule creation errors
    SCHEDULE_001 = "SCHEDULE_001"  # Video not found
    SCHEDULE_002 = "SCHEDULE_002"  # Invalid schedule datetime
    SCHEDULE_003 = "SCHEDULE_003"  # Schedule creation failed
    SCHEDULE_004 = "SCHEDULE_004"  # Schedule retrieval failed
    
    # Schedule cancellation errors
    SCHEDULE_005 = "SCHEDULE_005"  # Schedule cancellation failed
    
    # Validation errors
    VAL_001 = "VAL_001"  # Invalid input data
    VAL_002 = "VAL_002"  # Missing required field
    VAL_003 = "VAL_003"  # Invalid datetime format
    
    # Database errors
    DB_001 = "DB_001"  # Database connection error
    DB_002 = "DB_002"  # Database transaction error
    DB_003 = "DB_003"  # Database query error


@dataclass
class ScheduleCreationError(Exception):
    """Raised when schedule creation fails"""
    message: str
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "schedule_creation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ScheduleErrorCodes.SCHEDULE_003,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class ScheduleRetrievalError(Exception):
    """Raised when schedule retrieval fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "schedule_retrieval"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ScheduleErrorCodes.SCHEDULE_004,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class ScheduleCancellationError(Exception):
    """Raised when schedule cancellation fails"""
    message: str
    video_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "schedule_cancellation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ScheduleErrorCodes.SCHEDULE_005,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
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
            code=ScheduleErrorCodes.SCHEDULE_001,
            timestamp=datetime.now(),
            details={
                "video_id": self.video_id,
                "user_id": self.user_id,
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
            code=ScheduleErrorCodes.VAL_001,
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
            code=ScheduleErrorCodes.DB_002,
            timestamp=datetime.now(),
            details={
                "operation": self.operation,
                "error_type": self.error_type
            }
        )
