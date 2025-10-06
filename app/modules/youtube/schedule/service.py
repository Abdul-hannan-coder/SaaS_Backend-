from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from sqlmodel import Session, select
from ..video.model import Video
from .model import ScheduleRequest, ScheduleInfo
from .error_models import (
    ScheduleCreationError,
    ScheduleRetrievalError,
    ScheduleCancellationError,
    VideoNotFoundError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger

logger = get_logger("SCHEDULE_SERVICE")

def schedule_video_service(video_id: UUID, user_id: UUID, schedule_data: ScheduleRequest, db: Session) -> Dict[str, Any]:
    """
    Schedule a video for upload at a specific date and time.
    """
    # Get video from database with user ownership check
    statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found", video_id=str(video_id), user_id=str(user_id))
    
    # Get schedule datetime
    try:
        schedule_datetime = schedule_data.get_schedule_datetime()
    except ValueError as e:
        raise ValidationError(f"Invalid schedule datetime: {str(e)}", field="schedule_datetime", error_type="invalid_datetime")
    
    # Database operations
    try:
        # Update video with schedule information
        video.schedule_datetime = schedule_datetime
        video.privacy_status = schedule_data.privacy_status.value
        video.video_status = "scheduled"
        
        # Save changes to database
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Create schedule response
        schedule_info = _create_schedule_info(video, schedule_datetime)
        
        logger.info(f"Successfully scheduled video {video_id} for {schedule_datetime} with privacy {schedule_data.privacy_status.value}")
        
        return {
            "success": True,
            "message": "Video scheduled successfully",
            "video_id": str(video_id),
            "schedule_info": schedule_info
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error scheduling video: {str(e)}", operation="schedule_video", error_type="transaction")

def get_scheduled_videos_service(user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Get all scheduled videos for a user.
    """
    # Database operations
    try:
        # Get all scheduled videos for the user
        statement = select(Video).where(
            Video.user_id == user_id,
            Video.video_status == "scheduled",
            Video.schedule_datetime.is_not(None)
        ).order_by(Video.schedule_datetime)
        
        videos = db.exec(statement).all()
        
        scheduled_videos = []
        for video in videos:
            schedule_info = _create_schedule_info(video, video.schedule_datetime)
            scheduled_videos.append(schedule_info)
        
        logger.info(f"Successfully retrieved {len(scheduled_videos)} scheduled videos for user {user_id}")
        
        return {
            "success": True,
            "message": f"Retrieved {len(scheduled_videos)} scheduled videos",
            "user_id": str(user_id),
            "scheduled_videos": scheduled_videos,
            "count": len(scheduled_videos)
        }
        
    except Exception as e:
        raise ScheduleRetrievalError(f"Error getting scheduled videos: {str(e)}", user_id=str(user_id))

def cancel_schedule_service(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Cancel a scheduled video upload.
    """
    # Get video from database with user ownership check
    statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found", video_id=str(video_id), user_id=str(user_id))
    
    # Database operations
    try:
        # Reset schedule information
        video.schedule_datetime = None
        video.video_status = "ready"
        # Keep privacy status as it might be set separately
        
        # Save changes to database
        db.add(video)
        db.commit()
        db.refresh(video)
        
        logger.info(f"Successfully cancelled schedule for video {video_id}, user {user_id}")
        
        return {
            "success": True,
            "message": "Schedule cancelled successfully",
            "video_id": str(video_id),
            "user_id": str(user_id)
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error cancelling schedule: {str(e)}", operation="cancel_schedule", error_type="transaction")


def get_schedule_recommendations_service() -> Dict[str, Any]:
    """
    Get schedule time recommendations for better engagement.
    """
    current_time = datetime.now()
    
    recommendations = {
        "today": {
            "9:00": "Best for morning audience (high engagement)",
            "14:00": "Good for afternoon reach (students/workers on breaks)",
            "19:00": "Prime evening time (peak viewing hours)",
            "21:00": "Night owl time (late-night viewers)"
        },
        "tomorrow": {
            "9:00": "Morning engagement (early risers)",
            "14:00": "Afternoon reach (lunch breaks)",
            "19:00": "Evening peak (family time)"
        },
        "weekend": {
            "10:00": "Weekend family time (relaxed viewing)",
            "14:00": "Weekend afternoon (casual viewers)",
            "18:00": "Weekend evening (entertainment time)"
        }
    }
    
    return {
        "success": True,
        "message": "Schedule recommendations retrieved successfully",
        "recommendations": recommendations,
        "current_time": current_time.isoformat()
    } 




# ======================================
# ======================================

# Helper functions


# ======================================
# ======================================


def _create_schedule_info(video: Video, schedule_datetime: str) -> Dict[str, Any]:
    """
    Create schedule information for a video.
    
    Args:
        video: Video object
        schedule_datetime: Schedule datetime string
    
    Returns:
        Dict[str, Any]: Schedule information
    """
    try:
        # Parse schedule datetime
        schedule_dt = datetime.fromisoformat(schedule_datetime.replace('Z', '+00:00'))
        current_dt = datetime.now()
        
        # Calculate time until schedule
        time_diff = schedule_dt - current_dt
        time_until_schedule = _format_time_difference(time_diff)
        
        # Format schedule for display
        formatted_schedule = schedule_dt.strftime("%B %d, %Y at %I:%M %p")
        
        return {
            "video_id": str(video.id),
            "video_title": video.title or "Untitled",
            "schedule_datetime": schedule_datetime,
            "privacy_status": video.privacy_status,
            "video_status": video.video_status,
            "formatted_schedule": formatted_schedule,
            "time_until_schedule": time_until_schedule,
            "video_path": video.video_path
        }
        
    except Exception as e:
        logger.error(f"Error creating schedule info: {e}")
        return {}

def _format_time_difference(time_diff: timedelta) -> str:
    """
    Format time difference in a human-readable format.
    
    Args:
        time_diff: Time difference
    
    Returns:
        str: Formatted time difference
    """
    total_seconds = int(time_diff.total_seconds())
    
    if total_seconds < 0:
        return "Past due"
    
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    
    if days > 0:
        return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"