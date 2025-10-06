"""
Custom error models for user management using Pydantic and Dataclasses
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from datetime import datetime

# Error code constants for better maintainability
class ErrorCodes:
    # User-related errors
    USER_NOT_FOUND = "AUTH_001"
    USER_EMAIL_ALREADY_EXISTS = "AUTH_002"
    USER_USERNAME_ALREADY_EXISTS = "AUTH_003"
    USER_INVALID_CREDENTIALS = "AUTH_004"
    USER_ACCOUNT_DISABLED = "AUTH_005"
    USER_ACCOUNT_LOCKED = "AUTH_006"
    
    # Database-related errors
    DATABASE_CONNECTION_FAILED = "DB_001"
    DATABASE_QUERY_FAILED = "DB_002"
    DATABASE_TRANSACTION_FAILED = "DB_003"
    DATABASE_CONSTRAINT_VIOLATION = "DB_004"
    
    # Authentication-related errors
    AUTH_TOKEN_INVALID = "AUTH_007"
    AUTH_TOKEN_EXPIRED = "AUTH_008"
    AUTH_TOKEN_MISSING = "AUTH_009"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_010"
    
    # Validation-related errors
    VALIDATION_INVALID_EMAIL = "VAL_001"
    VALIDATION_INVALID_PASSWORD = "VAL_002"
    VALIDATION_INVALID_USERNAME = "VAL_003"
    VALIDATION_MISSING_REQUIRED_FIELD = "VAL_004"
    VALIDATION_FIELD_TOO_LONG = "VAL_005"
    VALIDATION_FIELD_TOO_SHORT = "VAL_006"

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
class UserNotFoundError(Exception):
    """Raised when user is not found"""
    message: str = "User not found"
    user_id: Optional[str] = None
    
    def __post_init__(self):
        self.error_detail = ErrorDetail(
            message=self.message,
            code=ErrorCodes.USER_NOT_FOUND,
            details={"user_id": self.user_id} if self.user_id else None
        )
        super().__init__(self.error_detail.message)

@dataclass
class UserAlreadyExistsError(Exception):
    """Raised when user already exists"""
    message: str = "User already exists"
    email: Optional[str] = None
    username: Optional[str] = None
    
    def __post_init__(self):
        details = {}
        error_code = ErrorCodes.USER_EMAIL_ALREADY_EXISTS  # Default
        
        if self.email:
            details["email"] = self.email
            error_code = ErrorCodes.USER_EMAIL_ALREADY_EXISTS
        if self.username:
            details["username"] = self.username
            error_code = ErrorCodes.USER_USERNAME_ALREADY_EXISTS
        if self.email and self.username:
            error_code = ErrorCodes.USER_EMAIL_ALREADY_EXISTS  # Email takes precedence
            
        self.error_detail = ErrorDetail(
            message=self.message,
            code=error_code,
            details=details if details else None
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
class AuthenticationError(Exception):
    """Raised when authentication fails"""
    message: str = "Authentication failed"
    reason: Optional[str] = None
    error_type: str = "invalid"  # invalid, expired, missing, insufficient_permissions
    
    def __post_init__(self):
        # Map error types to specific codes
        error_code_map = {
            "invalid": ErrorCodes.AUTH_TOKEN_INVALID,
            "expired": ErrorCodes.AUTH_TOKEN_EXPIRED,
            "missing": ErrorCodes.AUTH_TOKEN_MISSING,
            "insufficient_permissions": ErrorCodes.AUTH_INSUFFICIENT_PERMISSIONS
        }
        
        error_code = error_code_map.get(self.error_type, ErrorCodes.AUTH_TOKEN_INVALID)
        
        details = {}
        if self.reason:
            details["reason"] = self.reason
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
    error_type: str = "invalid"  # invalid_email, invalid_password, invalid_username, missing_field, too_long, too_short
    
    def __post_init__(self):
        # Map error types to specific codes
        error_code_map = {
            "invalid_email": ErrorCodes.VALIDATION_INVALID_EMAIL,
            "invalid_password": ErrorCodes.VALIDATION_INVALID_PASSWORD,
            "invalid_username": ErrorCodes.VALIDATION_INVALID_USERNAME,
            "missing_field": ErrorCodes.VALIDATION_MISSING_REQUIRED_FIELD,
            "too_long": ErrorCodes.VALIDATION_FIELD_TOO_LONG,
            "too_short": ErrorCodes.VALIDATION_FIELD_TOO_SHORT,
            "invalid": ErrorCodes.VALIDATION_INVALID_EMAIL  # Default
        }
        
        error_code = error_code_map.get(self.error_type, ErrorCodes.VALIDATION_INVALID_EMAIL)
        
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
