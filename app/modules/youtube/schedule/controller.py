from typing import Dict, Any
from uuid import UUID
from sqlmodel import Session
from pydantic import BaseModel

from .service import schedule_video_service, get_scheduled_videos_service, cancel_schedule_service, get_schedule_recommendations_service
from .model import ScheduleRequest
from ....utils.my_logger import get_logger

logger = get_logger("SCHEDULE_CONTROLLER")


class ScheduleResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]

def schedule_video_controller(video_id: UUID, user_id: UUID, schedule_data: ScheduleRequest, db: Session) -> ScheduleResponse:
    """
    Controller function to schedule a video for upload.
    """
    result = schedule_video_service(video_id, user_id, schedule_data, db)
    
    return ScheduleResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )

def get_scheduled_videos_controller(user_id: UUID, db: Session) -> ScheduleResponse:
    """
    Controller function to get all scheduled videos for a user.
    """
    result = get_scheduled_videos_service(user_id, db)
    
    return ScheduleResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )

def cancel_schedule_controller(video_id: UUID, user_id: UUID, db: Session) -> ScheduleResponse:
    """
    Controller function to cancel a scheduled video upload.
    """
    result = cancel_schedule_service(video_id, user_id, db)
    
    return ScheduleResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )

def get_schedule_recommendations_controller() -> ScheduleResponse:
    """
    Controller function to get schedule time recommendations.
    """
    result = get_schedule_recommendations_service()
    
    return ScheduleResponse(
        success=result["success"],
        message=result["message"],
        data=result
    ) 