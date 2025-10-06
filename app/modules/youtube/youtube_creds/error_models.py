"""
Error models for the YouTube credentials module
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


class YouTubeCredentialsErrorCodes:
    """Error codes for YouTube credentials-related operations"""
    # Credentials creation errors
    YT_CREDS_001 = "YT_CREDS_001"  # Credentials already exist
    YT_CREDS_002 = "YT_CREDS_002"  # Credentials creation failed
    YT_CREDS_003 = "YT_CREDS_003"  # Credentials not found
    YT_CREDS_004 = "YT_CREDS_004"  # Credentials retrieval failed
    YT_CREDS_005 = "YT_CREDS_005"  # Credentials update failed
    YT_CREDS_006 = "YT_CREDS_006"  # Credentials deletion failed
    YT_CREDS_007 = "YT_CREDS_007"  # Credentials validation failed
    
    # Validation errors
    VAL_001 = "VAL_001"  # Invalid input data
    VAL_002 = "VAL_002"  # Missing required field
    VAL_003 = "VAL_003"  # Invalid format
    
    # Database errors
    DB_001 = "DB_001"  # Database connection error
    DB_002 = "DB_002"  # Database transaction error
    DB_003 = "DB_003"  # Database query error


@dataclass
class YouTubeCredentialsAlreadyExistsError(Exception):
    """Raised when YouTube credentials already exist for a user"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "credentials_already_exists"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeCredentialsErrorCodes.YT_CREDS_001,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class YouTubeCredentialsNotFoundError(Exception):
    """Raised when YouTube credentials are not found"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "credentials_not_found"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeCredentialsErrorCodes.YT_CREDS_003,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class YouTubeCredentialsCreationError(Exception):
    """Raised when YouTube credentials creation fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "credentials_creation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeCredentialsErrorCodes.YT_CREDS_002,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class YouTubeCredentialsRetrievalError(Exception):
    """Raised when YouTube credentials retrieval fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "credentials_retrieval"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeCredentialsErrorCodes.YT_CREDS_004,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class YouTubeCredentialsUpdateError(Exception):
    """Raised when YouTube credentials update fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "credentials_update"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeCredentialsErrorCodes.YT_CREDS_005,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class YouTubeCredentialsDeletionError(Exception):
    """Raised when YouTube credentials deletion fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "credentials_deletion"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeCredentialsErrorCodes.YT_CREDS_006,
            timestamp=datetime.now(),
            details={
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
            code=YouTubeCredentialsErrorCodes.VAL_001,
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
            code=YouTubeCredentialsErrorCodes.DB_002,
            timestamp=datetime.now(),
            details={
                "operation": self.operation,
                "error_type": self.error_type
            }
        )
