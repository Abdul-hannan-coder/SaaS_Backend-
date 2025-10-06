"""
Title generator controller - handles HTTP concerns and maps service exceptions to HTTP responses
"""
from typing import Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException, status
from .service import (
    generate_video_title,
    update_video_title,
    regenerate_title,
    TitleResponse
)
from .error_models import (
    TitleGenerationError,
    VideoNotFoundError,
    VideoTranscriptNotFoundError,
    ApiKeyMissingError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger

logger = get_logger("TITLE_GENERATOR_CONTROLLER")

async def generate_title_for_video_controller(
    video_id: UUID,
    user_id: UUID,
    db: Session,
    user_requirements: Optional[str] = None,
    selected_title: Optional[str] = None,
    api_key: Optional[str] = None
) -> TitleResponse:
    """Generate title for a video using its transcript - HTTP layer only"""
    return await generate_video_title(video_id, user_id, db, user_requirements, selected_title, api_key)

async def save_video_title_controller(
    video_id: UUID,
    user_id: UUID,
    title: str,
    db: Session
) -> dict:
    """Save the generated title to the video record - HTTP layer only"""
    return await update_video_title(video_id, user_id, title, db)

async def regenerate_video_title_controller(
    video_id: UUID,
    user_id: UUID,
    db: Session,
    selected_title: Optional[str] = None
) -> TitleResponse:
    """Regenerate title for a video - HTTP layer only"""
    return await regenerate_title(video_id, user_id, db, selected_title) 