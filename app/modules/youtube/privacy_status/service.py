from typing import Dict, Any
from uuid import UUID
from sqlmodel import Session, select
from ..video.model import Video
from .model import PrivacyStatusRequest
from .error_models import (
    PrivacyStatusUpdateError,
    PrivacyStatusGetError,
    VideoNotFoundError,
    VideoAccessDeniedError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger

logger = get_logger("PRIVACY_STATUS_SERVICE")


def set_video_privacy_status(video_id: UUID, user_id: UUID, privacy_data: PrivacyStatusRequest, db: Session) -> Dict[str, Any]:
    """
    Set privacy status for a video.
    """
    # Validate privacy status
    if not privacy_data.privacy_status:
        raise ValidationError("Privacy status is required", field="privacy_status", error_type="missing_field")
    
    # Check if video exists and user has access
    statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found or you don't have permission to update it", video_id=str(video_id), user_id=str(user_id))
    
    # Database operations
    try:
        # Update privacy status in the database
        video.privacy_status = privacy_data.privacy_status.value
        
        # Save changes to database
        db.add(video)
        db.commit()
        db.refresh(video)
        
        logger.info(f"Successfully set privacy status for video {video_id}, user {user_id}: {privacy_data.privacy_status.value}")
        
        return {
            "success": True,
            "message": "Privacy status updated successfully",
            "privacy_status": video.privacy_status,
            "video_id": str(video_id),
            "user_id": str(user_id)
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error setting privacy status: {str(e)}", operation="set_video_privacy_status", error_type="transaction")


def get_video_privacy_status(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Get current privacy status for a video.
    """
    # Check if video exists and user has access
    statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found or you don't have permission to access it", video_id=str(video_id), user_id=str(user_id))
    
    # Database operations
    try:
        logger.info(f"Successfully retrieved privacy status for video {video_id}, user {user_id}")
        
        return {
            "success": True,
            "message": "Privacy status retrieved successfully",
            "video_id": str(video_id),
            "user_id": str(user_id),
            "video_status": video.video_status or "not_set",
            "privacy_status": video.privacy_status,
            "schedule_datetime": video.schedule_datetime,
            "video_title": video.title,
            "video_path": video.video_path
        }
        
    except Exception as e:
        raise DatabaseError(f"Error getting privacy status: {str(e)}", operation="get_video_privacy_status", error_type="transaction")