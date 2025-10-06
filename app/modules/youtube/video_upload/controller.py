"""
Controller layer for video upload management
"""
from typing import Dict, Any
from uuid import UUID
from sqlmodel import Session
from pydantic import BaseModel

from .service import upload_video_to_youtube_service
from ....utils.my_logger import get_logger

logger = get_logger("YOUTUBE_UPLOAD_CONTROLLER")


class VideoUploadControllerResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]


def upload_video_controller(video_id: UUID, user_id: UUID, db: Session) -> VideoUploadControllerResponse:
    """
    Controller function to upload a video to YouTube.
    
    Args:
        video_id: UUID of the video to upload
        user_id: UUID of the user
        db: Database session
    
    Returns:
        VideoUploadControllerResponse: Upload result response
    """
    result = upload_video_to_youtube_service(video_id, user_id, db)
    
    return VideoUploadControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )