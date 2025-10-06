"""
Controller layer for video management
"""
from typing import List, Dict, Any
from uuid import UUID
from fastapi import UploadFile, BackgroundTasks
from sqlmodel import Session
from pydantic import BaseModel

from .service import (
    upload_video_service,
    get_user_videos_service,
    get_video_by_id_service,
    download_and_store_video_service,
    update_video_service
)
from .model import VideoResponse, VideoUpdate
from ....utils.my_logger import get_logger

logger = get_logger("VIDEO_CONTROLLER")


class VideoControllerResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]


async def upload_video_controller(
    file: UploadFile,
    user_id: UUID,
    db: Session,
    background_tasks: BackgroundTasks
) -> VideoControllerResponse:
    """Upload video file and store path in database"""
    result = await upload_video_service(file, user_id, db, background_tasks)
    
    return VideoControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )


def get_user_videos_controller(user_id: UUID, db: Session) -> VideoControllerResponse:
    """Get all videos for a specific user"""
    result = get_user_videos_service(user_id, db)
    
    return VideoControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )


def get_video_by_id_controller(video_id: UUID, user_id: UUID, db: Session) -> VideoControllerResponse:
    """Get a specific video by ID for a user"""
    result = get_video_by_id_service(video_id, user_id, db)
    
    return VideoControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )


async def download_and_store_video_controller(
    video_url: str,
    user_id: UUID,
    db: Session,
    background_tasks: BackgroundTasks
) -> VideoControllerResponse:
    """Download video from URL and store path in database"""
    result = await download_and_store_video_service(video_url, user_id, db, background_tasks)
    
    return VideoControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )


def update_video_controller(
    video_id: UUID,
    user_id: UUID,
    video_update: VideoUpdate,
    db: Session
) -> VideoControllerResponse:
    """Update a specific video by ID for a user"""
    result = update_video_service(video_id, user_id, video_update, db)
    
    return VideoControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )