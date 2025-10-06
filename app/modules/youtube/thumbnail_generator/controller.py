from typing import Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import UploadFile
from pydantic import BaseModel

from .service import (
    generate_video_thumbnail,
    save_video_thumbnail,
    upload_custom_thumbnail
)
from ....utils.my_logger import get_logger

logger = get_logger("THUMBNAIL_GENERATOR_CONTROLLER")


class ThumbnailResponse(BaseModel):
    """Response model for thumbnail generation"""
    success: bool
    message: str
    video_id: str
    image_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    prompt: Optional[str] = None
    model: Optional[str] = None
    seed: Optional[int] = None


async def generate_thumbnail_for_video_controller(
    video_id: UUID,
    user_id: UUID,
    db: Session
) -> ThumbnailResponse:
    """
    Generate thumbnail image URL for a video using its transcript - HTTP layer only
    """
    result = await generate_video_thumbnail(video_id, user_id, db)
    
    return ThumbnailResponse(
        success=result["success"],
        message=result["message"],
        video_id=result["video_id"],
        image_url=result.get("image_url"),
        width=result.get("width"),
        height=result.get("height"),
        prompt=result.get("prompt"),
        model=result.get("model"),
        seed=result.get("seed")
    )


async def save_video_thumbnail_controller(
    video_id: UUID,
    user_id: UUID,
    thumbnail_url: str,
    db: Session
) -> dict:
    """
    Save the thumbnail URL to the video record - HTTP layer only
    """
    return await save_video_thumbnail(video_id, user_id, thumbnail_url, db)


async def upload_custom_thumbnail_controller(
    video_id: UUID,
    user_id: UUID,
    file: UploadFile,
    db: Session
) -> dict:
    """
    Upload and save a custom thumbnail file - HTTP layer only
    """
    # Read file content
    file_content = await file.read()
    
    return await upload_custom_thumbnail(
        video_id=video_id,
        user_id=user_id,
        file_content=file_content,
        filename=file.filename or "thumbnail",
        db=db
    )