"""
Error models for the YouTube token module
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


class YouTubeTokenErrorCodes:
    """Error codes for YouTube token-related operations"""
    # Token creation errors
    TOKEN_001 = "TOKEN_001"  # Token creation failed
    TOKEN_002 = "TOKEN_002"  # Token not found
    TOKEN_003 = "TOKEN_003"  # Token retrieval failed
    TOKEN_004 = "TOKEN_004"  # Token update failed
    TOKEN_005 = "TOKEN_005"  # Token deletion failed
    TOKEN_006 = "TOKEN_006"  # Token refresh failed
    TOKEN_007 = "TOKEN_007"  # Token validation failed
    TOKEN_008 = "TOKEN_008"  # OAuth callback failed
    TOKEN_009 = "TOKEN_009"  # OAuth URL generation failed
    
    # OAuth errors
    OAUTH_001 = "OAUTH_001"  # OAuth authorization failed
    OAUTH_002 = "OAUTH_002"  # OAuth token exchange failed
    OAUTH_003 = "OAUTH_003"  # OAuth callback error
    OAUTH_004 = "OAUTH_004"  # OAuth state mismatch
    
    # API errors
    API_001 = "API_001"  # Google API error
    API_002 = "API_002"  # API request failed
    API_003 = "API_003"  # API response invalid
    
    # Validation errors
    VAL_001 = "VAL_001"  # Invalid input data
    VAL_002 = "VAL_002"  # Missing required field
    VAL_003 = "VAL_003"  # Invalid token format
    
    # Database errors
    DB_001 = "DB_001"  # Database connection error
    DB_002 = "DB_002"  # Database transaction error
    DB_003 = "DB_003"  # Database query error


@dataclass
class TokenCreationError(Exception):
    """Raised when token creation fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "token_creation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeTokenErrorCodes.TOKEN_001,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class TokenNotFoundError(Exception):
    """Raised when token is not found"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "token_not_found"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeTokenErrorCodes.TOKEN_002,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class TokenRetrievalError(Exception):
    """Raised when token retrieval fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "token_retrieval"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeTokenErrorCodes.TOKEN_003,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class TokenRefreshError(Exception):
    """Raised when token refresh fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "token_refresh"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeTokenErrorCodes.TOKEN_006,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class OAuthCallbackError(Exception):
    """Raised when OAuth callback fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "oauth_callback"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeTokenErrorCodes.OAUTH_003,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class OAuthUrlGenerationError(Exception):
    """Raised when OAuth URL generation fails"""
    message: str
    user_id: Optional[str] = None
    error_type: str = "oauth_url_generation"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeTokenErrorCodes.OAUTH_004,
            timestamp=datetime.now(),
            details={
                "user_id": self.user_id,
                "error_type": self.error_type
            }
        )


@dataclass
class GoogleApiError(Exception):
    """Raised when Google API operations fail"""
    message: str
    api_endpoint: Optional[str] = None
    user_id: Optional[str] = None
    error_type: str = "google_api"
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=YouTubeTokenErrorCodes.API_001,
            timestamp=datetime.now(),
            details={
                "api_endpoint": self.api_endpoint,
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
            code=YouTubeTokenErrorCodes.VAL_001,
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
            code=YouTubeTokenErrorCodes.DB_002,
            timestamp=datetime.now(),
            details={
                "operation": self.operation,
                "error_type": self.error_type
            }
        )
