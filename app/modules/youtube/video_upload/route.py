from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path, Body, Query
from sqlmodel import Session
from pydantic import BaseModel

from .controller import upload_video_controller, VideoUploadControllerResponse
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp
from ....utils.my_logger import get_logger

logger = get_logger("YOUTUBE_UPLOAD_ROUTES")

router = APIRouter(prefix="/youtube-upload", tags=["Youtube Upload"])

# Request/Response models - using VideoUploadControllerResponse from controller

@router.post("/{video_id}/upload", response_model=VideoUploadControllerResponse)
async def upload_video(
    video_id: UUID = Path(..., description="The ID of the video to upload"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideoUploadControllerResponse:
    """
    Upload a video to YouTube.
    
    This endpoint uploads a video to YouTube with all the metadata from the database:
    - Title, description, and transcript
    - Privacy settings and scheduling
    - Automatic playlist addition (if playlist_name is set in database)
    - Automatic custom thumbnail upload (if thumbnail_path exists in database)
    
    Args:
        video_id: The UUID of the video to upload
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        UploadResponse: Upload result with YouTube video ID and URL
        
    Raises:
        HTTPException: If upload fails or other errors occur
    """
    return upload_video_controller(video_id, current_user.id, db) 