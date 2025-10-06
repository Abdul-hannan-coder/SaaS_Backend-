"""
Service layer for YouTube credentials management
"""
from sqlmodel import Session, select
from uuid import UUID
from typing import Optional, Dict, Any

from .model import (
    YouTubeCredentials,
    YouTubeCredentialsCreate,
    YouTubeCredentialsUpdate,
    YouTubeCredentialsResponse,
    YouTubeCredentialsStatus
)
from .error_models import (
    YouTubeCredentialsAlreadyExistsError,
    YouTubeCredentialsNotFoundError,
    YouTubeCredentialsCreationError,
    YouTubeCredentialsRetrievalError,
    YouTubeCredentialsUpdateError,
    YouTubeCredentialsDeletionError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger

logger = get_logger("YOUTUBE_CREDENTIALS_SERVICE")


def create_youtube_credentials_service(
    user_id: UUID,
    client_id: str,
    client_secret: str,
    db: Session
) -> Dict[str, Any]:
    """Create YouTube credentials for a user"""
    # Validate input
    if not client_id or not client_secret:
        raise ValidationError("Client ID and Client Secret are required", field="credentials", error_type="missing_field")
    
    # Check if user already has credentials
    existing_credentials = db.exec(
        select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
    ).first()
    
    if existing_credentials:
        raise YouTubeCredentialsAlreadyExistsError("YouTube credentials already exist for this user", user_id=str(user_id))
    
    # Database operations
    try:
        # Create new credentials
        credentials = YouTubeCredentials(
            user_id=user_id,
            client_id=client_id,
            client_secret=client_secret,
            is_active=True
        )
        
        db.add(credentials)
        db.commit()
        db.refresh(credentials)
        
        logger.info(f"Successfully created YouTube credentials for user_id: {user_id}")
        
        return {
            "success": True,
            "message": "YouTube credentials created successfully",
            "user_id": str(user_id),
            "credentials": YouTubeCredentialsResponse(
                id=credentials.id,
                user_id=credentials.user_id,
                client_id_preview=credentials.client_id[:10] + "..." + credentials.client_id[-4:] if len(credentials.client_id) > 14 else credentials.client_id,
                client_secret_preview=credentials.client_secret[:10] + "..." + credentials.client_secret[-4:] if len(credentials.client_secret) > 14 else credentials.client_secret,
                is_active=credentials.is_active,
                created_at=credentials.created_at,
                updated_at=credentials.updated_at
            ).dict()
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error creating YouTube credentials: {str(e)}", operation="create_credentials", error_type="transaction")


def get_youtube_credentials_service(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Get YouTube credentials for a user"""
    # Database operations
    try:
        credentials = db.exec(
            select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
        ).first()
        
        if not credentials:
            raise YouTubeCredentialsNotFoundError("YouTube credentials not found for this user", user_id=str(user_id))
        
        logger.info(f"Successfully retrieved YouTube credentials for user_id: {user_id}")
        
        return {
            "success": True,
            "message": "YouTube credentials retrieved successfully",
            "user_id": str(user_id),
            "credentials": YouTubeCredentialsResponse(
                id=credentials.id,
                user_id=credentials.user_id,
                client_id_preview=credentials.client_id[:10] + "..." + credentials.client_id[-4:] if len(credentials.client_id) > 14 else credentials.client_id,
                client_secret_preview=credentials.client_secret[:10] + "..." + credentials.client_secret[-4:] if len(credentials.client_secret) > 14 else credentials.client_secret,
                is_active=credentials.is_active,
                created_at=credentials.created_at,
                updated_at=credentials.updated_at
            ).dict()
        }
        
    except Exception as e:
        if isinstance(e, YouTubeCredentialsNotFoundError):
            raise
        raise DatabaseError(f"Error retrieving YouTube credentials: {str(e)}", operation="get_credentials", error_type="query")


def update_youtube_credentials_service(
    user_id: UUID,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = None
) -> Dict[str, Any]:
    """Update YouTube credentials for a user"""
    # Database operations
    try:
        credentials = db.exec(
            select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
        ).first()
        
        if not credentials:
            raise YouTubeCredentialsNotFoundError("YouTube credentials not found for this user", user_id=str(user_id))
        
        # Update fields if provided
        if client_id is not None:
            credentials.client_id = client_id
        if client_secret is not None:
            credentials.client_secret = client_secret
        if is_active is not None:
            credentials.is_active = is_active
        
        db.add(credentials)
        db.commit()
        db.refresh(credentials)
        
        logger.info(f"Successfully updated YouTube credentials for user_id: {user_id}")
        
        return {
            "success": True,
            "message": "YouTube credentials updated successfully",
            "user_id": str(user_id),
            "credentials": YouTubeCredentialsResponse(
                id=credentials.id,
                user_id=credentials.user_id,
                client_id_preview=credentials.client_id[:10] + "..." + credentials.client_id[-4:] if len(credentials.client_id) > 14 else credentials.client_id,
                client_secret_preview=credentials.client_secret[:10] + "..." + credentials.client_secret[-4:] if len(credentials.client_secret) > 14 else credentials.client_secret,
                is_active=credentials.is_active,
                created_at=credentials.created_at,
                updated_at=credentials.updated_at
            ).dict()
        }
        
    except Exception as e:
        db.rollback()
        if isinstance(e, YouTubeCredentialsNotFoundError):
            raise
        raise DatabaseError(f"Error updating YouTube credentials: {str(e)}", operation="update_credentials", error_type="transaction")


def delete_youtube_credentials_service(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Delete YouTube credentials for a user"""
    # Database operations
    try:
        credentials = db.exec(
            select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
        ).first()
        
        if not credentials:
            raise YouTubeCredentialsNotFoundError("YouTube credentials not found for this user", user_id=str(user_id))
        
        db.delete(credentials)
        db.commit()
        
        logger.info(f"Successfully deleted YouTube credentials for user_id: {user_id}")
        
        return {
            "success": True,
            "message": "YouTube credentials deleted successfully",
            "user_id": str(user_id)
        }
        
    except Exception as e:
        db.rollback()
        if isinstance(e, YouTubeCredentialsNotFoundError):
            raise
        raise DatabaseError(f"Error deleting YouTube credentials: {str(e)}", operation="delete_credentials", error_type="transaction")


def get_youtube_credentials_status_service(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Get YouTube credentials status for a user"""
    # Database operations
    try:
        credentials = db.exec(
            select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
        ).first()
        
        if not credentials:
            return {
                "success": True,
                "message": "No YouTube credentials found",
                "user_id": str(user_id),
                "status": YouTubeCredentialsStatus(
                    has_credentials=False,
                    is_active=False,
                    message="No credentials configured"
                ).dict()
            }
        
        logger.info(f"Successfully retrieved YouTube credentials status for user_id: {user_id}")
        
        return {
            "success": True,
            "message": "YouTube credentials status retrieved successfully",
            "user_id": str(user_id),
            "status": YouTubeCredentialsStatus(
                has_credentials=True,
                is_active=credentials.is_active,
                message="Credentials are configured and active" if credentials.is_active else "Credentials are configured but inactive"
            ).dict()
        }
        
    except Exception as e:
        raise DatabaseError(f"Error retrieving YouTube credentials status: {str(e)}", operation="get_credentials_status", error_type="query")
