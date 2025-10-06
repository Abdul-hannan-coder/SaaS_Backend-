"""
All-in-one video processing routes
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from .controller import process_video_all_in_one_controller, save_generated_content_controller
from .model import AllInOneRequest, AllInOneResponse, SaveContentRequest, SaveContentResponse
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp

router = APIRouter(prefix="/all-in-one", tags=["All In One Processing"])


@router.post("/{video_id}/process", response_model=AllInOneResponse)
async def process_video_all_in_one_endpoint(
    video_id: str,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Process a video with all available generation features in one API call
    
    This endpoint automatically generates:
    - Video titles
    - Video descriptions  
    - Video timestamps
    - Video thumbnails (5 thumbnails)
    
    Args:
        video_id: Video ID (UUID or YouTube ID) to process
    
    Returns: Complete processing results with success/failure status for each task
    """
    return await process_video_all_in_one_controller(
        video_id=video_id,
        user_id=current_user.id,
        db=db
    )


@router.post("/{video_id}/save-content", response_model=SaveContentResponse)
async def save_generated_content_endpoint(
    video_id: str,
    request: SaveContentRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Save selected generated content to video record
    
    This endpoint allows you to:
    - Save a selected title from generated titles
    - Download and save a selected thumbnail from generated thumbnail URLs
    - Save generated description and timestamps
    
    Args:
        video_id: Video ID (UUID or YouTube ID) to update
        request: Contains selected_title, selected_thumbnail_url, and save options
    
    Returns: Success status and details of saved content
    """
    return await save_generated_content_controller(
        request=request,
        video_id=video_id,
        user_id=current_user.id,
        db=db
    )
