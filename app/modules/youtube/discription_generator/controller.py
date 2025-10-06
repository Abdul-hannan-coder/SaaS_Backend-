from typing import Optional
from uuid import UUID
from sqlmodel import Session
from pydantic import BaseModel

from .service import (
    generate_video_description,
    save_video_description,
    regenerate_video_description
)
from ....utils.my_logger import get_logger

logger = get_logger("DESCRIPTION_GENERATOR_CONTROLLER")

class DescriptionResponse(BaseModel):
    """Response model for description generation"""
    video_id: UUID
    generated_description: str
    success: bool
    message: str


async def generate_description_for_video_controller(
    video_id: UUID,
    user_id: UUID,
    db: Session,
    custom_template: Optional[str] = None
) -> DescriptionResponse:
    """
    Generate description for a video using its transcript - HTTP layer only
    """
    result = await generate_video_description(video_id, user_id, db, custom_template)
    
    return DescriptionResponse(
        video_id=result["video_id"],
        generated_description=result["generated_description"],
        success=result["success"],
        message=result["message"]
    )

async def save_video_description_controller(
    video_id: UUID,
    user_id: UUID,
    description: str,
    db: Session
) -> dict:
    """
    Save the generated description to the video record - HTTP layer only
    """
    return await save_video_description(video_id, user_id, description, db)

async def regenerate_video_description_controller(
    video_id: UUID,
    user_id: UUID,
    db: Session,
    custom_template: Optional[str] = None
) -> DescriptionResponse:
    """
    Regenerate description for a video - HTTP layer only
    """
    result = await regenerate_video_description(video_id, user_id, db, custom_template)
    
    return DescriptionResponse(
        video_id=result["video_id"],
        generated_description=result["generated_description"],
        success=result["success"],
        message=result["message"]
    ) 