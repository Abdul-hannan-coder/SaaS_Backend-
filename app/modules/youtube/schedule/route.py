from typing import Dict, Any, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path, Body
from sqlmodel import Session

from .controller import (
    schedule_video_controller, 
    get_scheduled_videos_controller, 
    cancel_schedule_controller,
    get_schedule_recommendations_controller,
    ScheduleResponse
)
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp
from .model import ScheduleRequest
from ....utils.my_logger import get_logger

logger = get_logger("SCHEDULE_ROUTES")

router = APIRouter(prefix="/schedule", tags=["Schedule Video"])

@router.post("/{video_id}/schedule", response_model=ScheduleResponse)
async def schedule_video(
    video_id: UUID = Path(..., description="The ID of the video"),
    schedule_data: ScheduleRequest = Body(..., description="Schedule date, time, and privacy status"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> ScheduleResponse:
    """
    Schedule a video for upload at a specific date and time.
    
    This endpoint allows users to schedule their videos with:
    - Specific date (YYYY-MM-DD)
    - Specific time (HH:MM in 24-hour format)
    - Privacy status (private, public, unlisted)
    
    Args:
        video_id: The UUID of the video
        schedule_data: ScheduleRequest containing date, time, and privacy status
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        ScheduleResponse: Schedule information with formatted display
    
    Raises:
        HTTPException: If video not found or other errors occur
    """
    logger.info(f"Schedule video request received for video_id: {video_id}, user_id: {current_user.id}")
    return schedule_video_controller(video_id, current_user.id, schedule_data, db)

@router.get("/my-scheduled-videos", response_model=ScheduleResponse)
async def get_my_scheduled_videos(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> ScheduleResponse:
    """
    Get all scheduled videos for the authenticated user.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        Dict[str, Any]: List of scheduled videos with timing information
        
    Raises:
        HTTPException: If retrieval fails or other errors occur
    """
    logger.info(f"Get scheduled videos request received for user_id: {current_user.id}")
    return get_scheduled_videos_controller(current_user.id, db)

@router.delete("/{video_id}/cancel", response_model=ScheduleResponse)
async def cancel_scheduled_video(
    video_id: UUID = Path(..., description="The ID of the video"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> ScheduleResponse:
    """
    Cancel a scheduled video upload.
    
    Args:
        video_id: The UUID of the video
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        Dict[str, Any]: Cancellation confirmation
        
    Raises:
        HTTPException: If video not found or other errors occur
    """
    logger.info(f"Cancel schedule request received for video_id: {video_id}, user_id: {current_user.id}")
    return cancel_schedule_controller(video_id, current_user.id, db)

@router.get("/recommendations", response_model=ScheduleResponse)
async def get_schedule_recommendations(
    current_user: UserSignUp = Depends(get_current_user)
) -> ScheduleResponse:
    """
    Get schedule time recommendations for better engagement.
    
    Args:
        current_user: The authenticated user from JWT token
    
    Returns:
        Dict[str, Any]: Schedule time recommendations
        
    Raises:
        HTTPException: If retrieval fails or other errors occur
    """
    logger.info(f"Schedule recommendations request received for user_id: {current_user.id}")
    return get_schedule_recommendations_controller() 