"""
Controller layer for single video details
"""
from typing import Dict, Any
from uuid import UUID
from fastapi import UploadFile, File
from sqlmodel import Session
from pydantic import BaseModel

from .service import get_single_video_details_service, update_video_details_service, delete_video_service,upload_custom_thumbnail_service,select_generated_thumbnail_service,update_thumbnail_service
from .model import SingleVideoDetailsResponse, UpdateVideoRequest, UpdateVideoResponse, DeleteVideoResponse, ThumbnailUpdateResponse
from ....utils.my_logger import get_logger

logger = get_logger("SINGLE_VIDEO_CONTROLLER")


class SingleVideoControllerResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]


def get_single_video_details_controller(video_id: str, user_id: UUID, db: Session, refresh: bool = False) -> SingleVideoControllerResponse:
    """Get video details by video ID for a specific user"""
    result = get_single_video_details_service(video_id, user_id, db, refresh)
    
    return SingleVideoControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )


def update_video_details_controller(video_id: str, user_id: UUID, db: Session, update_data: UpdateVideoRequest) -> UpdateVideoResponse:
    """Update video details for a specific user"""
    result = update_video_details_service(video_id, user_id, db, update_data)
    
    return UpdateVideoResponse(
        success=result["success"],
        message=result["message"],
        updated_fields=result["updated_fields"],
        video_details=result["video_details"]
    )


def delete_video_controller(video_id: str, user_id: UUID, db: Session) -> DeleteVideoResponse:
    """Delete video for a specific user"""
    result = delete_video_service(video_id, user_id, db)
    
    return DeleteVideoResponse(
        success=result["success"],
        message=result["message"],
        deleted_video_id=result["deleted_video_id"]
    )

async def upload_custom_thumbnail_controller(video_id: str, file: UploadFile , dir_path: str , user_id: UUID, db: Session) -> ThumbnailUpdateResponse:
    """Upload custom thumbnail for a specific user"""
    result = await upload_custom_thumbnail_service(video_id, file, dir_path, user_id, db)
    
    return ThumbnailUpdateResponse(
        success=result["success"],
        message=result["message"],
        video_id=result["video_id"],
        thumbnail_url=result["thumbnail_url"],
        method_used=result["method_used"]
    )


async def update_thumbnail_controller(video_id: str, user_id: UUID, db: Session) -> ThumbnailUpdateResponse:
    """Update a thumbnail for a video"""
    result = await update_thumbnail_service(video_id, user_id, db)
    
    return ThumbnailUpdateResponse(
        success=result["success"],
        message=result["message"],
        video_id=result["video_id"],
        thumbnail_url=result["thumbnail_url"],
        method_used=result["method_used"]
    )

async def select_generated_thumbnail_controller(video_id: str, url:str, user_id: UUID, db: Session, dir_path: str) -> ThumbnailUpdateResponse:
    """Select a generated thumbnail and update the database"""
    result = await select_generated_thumbnail_service(video_id, url, user_id, db, dir_path)
    
    return ThumbnailUpdateResponse(
        success=result["success"],
        message=result["message"],
        video_id=result["video_id"],
        thumbnail_url=result["thumbnail_url"],
        method_used=result["method_used"]
    )