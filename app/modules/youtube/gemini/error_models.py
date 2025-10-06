"""
Custom error models for Gemini API key management using Pydantic and Dataclasses
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from datetime import datetime

# Error code constants for better maintainability
class ErrorCodes:
    # Gemini-related errors
    GEMINI_KEY_NOT_FOUND = "GEM_001"
    GEMINI_KEY_ALREADY_EXISTS = "GEM_002"
    GEMINI_KEY_INVALID = "GEM_003"
    GEMINI_KEY_INACTIVE = "GEM_004"
    GEMINI_API_ERROR = "GEM_005"
    
    # Database-related errors
    DATABASE_CONNECTION_FAILED = "DB_001"
    DATABASE_QUERY_FAILED = "DB_002"
    DATABASE_TRANSACTION_FAILED = "DB_003"
    DATABASE_CONSTRAINT_VIOLATION = "DB_004"
    
    # Validation-related errors
    VALIDATION_INVALID_API_KEY = "VAL_001"
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
class GeminiKeyNotFoundError(Exception):
    """Raised when Gemini key is not found"""
    message: str = "Gemini API key not found"
    user_id: Optional[str] = None
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ErrorCodes.GEMINI_KEY_NOT_FOUND,
            details={"user_id": self.user_id} if self.user_id else None
        )
        super().__init__(self.error_detail.message)

@dataclass
class GeminiKeyAlreadyExistsError(Exception):
    """Raised when Gemini key already exists"""
    message: str = "Gemini API key already exists"
    user_id: Optional[str] = None
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ErrorCodes.GEMINI_KEY_ALREADY_EXISTS,
            details={"user_id": self.user_id} if self.user_id else None
        )
        super().__init__(self.error_detail.message)

@dataclass
class GeminiKeyInvalidError(Exception):
    """Raised when Gemini key is invalid"""
    message: str = "Invalid Gemini API key"
    user_id: Optional[str] = None
    error_type: str = "invalid"  # invalid, inactive, expired
    
    def __post_init__(self):
        # Map error types to specific codes
        error_code_map = {
            "invalid": ErrorCodes.GEMINI_KEY_INVALID,
            "inactive": ErrorCodes.GEMINI_KEY_INACTIVE,
            "expired": ErrorCodes.GEMINI_KEY_INVALID
        }
        
        error_code = error_code_map.get(self.error_type, ErrorCodes.GEMINI_KEY_INVALID)
        
        details = {}
        if self.user_id:
            details["user_id"] = self.user_id
        details["error_type"] = self.error_type
            
        self.error_detail = ErrorDetail(
            message=self.message,
            code=error_code,
            details=details
        )
        super().__init__(self.error_detail.message)

@dataclass
class GeminiApiError(Exception):
    """Raised when Gemini API call fails"""
    message: str = "Gemini API error"
    operation: Optional[str] = None
    error_type: str = "api_error"  # api_error, rate_limit, quota_exceeded
    
    def __post_init__(self):
        details = {}
        if self.operation:
            details["operation"] = self.operation
        details["error_type"] = self.error_type
            
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ErrorCodes.GEMINI_API_ERROR,
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

@dataclass
class ValidationError(Exception):
    """Raised when input validation fails"""
    message: str = "Validation failed"
    field: Optional[str] = None
    value: Optional[Any] = None
    error_type: str = "invalid"  # invalid_api_key, missing_field, too_long, too_short
    
    def __post_init__(self):
        # Map error types to specific codes
        error_code_map = {
            "invalid_api_key": ErrorCodes.VALIDATION_INVALID_API_KEY,
            "missing_field": ErrorCodes.VALIDATION_MISSING_REQUIRED_FIELD,
            "too_long": ErrorCodes.VALIDATION_FIELD_TOO_LONG,
            "too_short": ErrorCodes.VALIDATION_FIELD_TOO_SHORT,
            "invalid": ErrorCodes.VALIDATION_INVALID_API_KEY  # Default
        }
        
        error_code = error_code_map.get(self.error_type, ErrorCodes.VALIDATION_INVALID_API_KEY)
        
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
