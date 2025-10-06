from typing import Optional
from uuid import UUID
from sqlmodel import Session
from pydantic import BaseModel

from .service import (
    generate_video_timestamps,
    save_video_timestamps,
    regenerate_video_timestamps
)
from ....utils.my_logger import get_logger

logger = get_logger("TIMESTAMPS_GENERATOR_CONTROLLER")


class TimeStampsResponse(BaseModel):
    """Response model for timestamps generation"""
    video_id: UUID
    generated_timestamps: str
    success: bool
    message: str


async def generate_timestamps_for_video_controller(
    video_id: UUID,
    user_id: UUID,
    db: Session
) -> TimeStampsResponse:
    """
    Generate timestamps for a video using its transcript - HTTP layer only
    """
    result = await generate_video_timestamps(video_id, user_id, db)
    
    return TimeStampsResponse(
        video_id=UUID(result["video_id"]),
        generated_timestamps=result["generated_timestamps"],
        success=result["success"],
        message=result["message"]
    )


async def save_video_timestamps_controller(
    video_id: UUID,
    user_id: UUID,
    timestamps: str,
    db: Session
) -> dict:
    """
    Save the timestamps to the video record - HTTP layer only
    """
    return await save_video_timestamps(video_id, user_id, timestamps, db)


async def regenerate_video_timestamps_controller(
    video_id: UUID,
    user_id: UUID,
    db: Session
) -> TimeStampsResponse:
    """
    Regenerate timestamps for a video using its transcript - HTTP layer only
    """
    result = await regenerate_video_timestamps(video_id, user_id, db)
    
    return TimeStampsResponse(
        video_id=UUID(result["video_id"]),
        generated_timestamps=result["generated_timestamps"],
        success=result["success"],
        message=result["message"]
    )
