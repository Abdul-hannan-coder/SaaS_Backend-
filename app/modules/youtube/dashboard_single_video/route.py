from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlmodel import Session
from uuid import UUID

from .controller import upload_custom_thumbnail_controller

from .controller import (
    get_single_video_details_controller,
    update_video_details_controller,
    delete_video_controller,
    select_generated_thumbnail_controller,
    update_thumbnail_controller,
    SingleVideoControllerResponse,
)
from .model import UpdateVideoRequest, UpdateVideoResponse, DeleteVideoResponse, ThumbnailUpdateResponse
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp
from ..helpers.thumbnail_generation import generate_video_thumbnail
from .model import SingleVideoDetails



router = APIRouter(prefix="/single-video", tags=["Dashboard Single Video"])







@router.get("/{video_id}", response_model=SingleVideoControllerResponse)
async def get_single_video_details(
    video_id: str,
    refresh: bool = False,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get video details by video ID for the authenticated user
    
    Args:
        video_id: YouTube video ID or database UUID
        refresh: If True, fetch fresh data from YouTube API and update database
                If False, return data from database only
    
    Returns: title, description, thumbnail_link, playlist, privacy_status
    """
    return get_single_video_details_controller(video_id, current_user.id, db, refresh)


@router.put("/{video_id}", response_model=UpdateVideoResponse)
async def update_single_video_details(
    video_id: str,
    update_data: UpdateVideoRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Update video details on YouTube for the authenticated user
    
    Args:
        video_id: YouTube video ID
        update_data: Fields to update (title, description, privacy_status, playlist_id, remove_from_playlist)
    
    Returns: success status, updated fields, and updated video details
    """
    return update_video_details_controller(video_id, current_user.id, db, update_data)


@router.delete("/{video_id}", response_model=DeleteVideoResponse)
async def delete_single_video(
    video_id: str,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    ⚠️ PERMANENTLY DELETE video from YouTube for the authenticated user
    
    Args:
        video_id: YouTube video ID
    
    Returns: success status and deleted video ID
    
    WARNING: This action is IRREVERSIBLE! The video will be permanently deleted from YouTube.
    """
    return delete_video_controller(video_id, current_user.id, db)


# generate thumbnail
@router.post("/{video_id}/generate-thumbnail", response_model=ThumbnailUpdateResponse)
async def generate_video_thumbnail_endpoint(
    video_id: str,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Generate thumbnail for a video
    """
    # sql to get transcript
    statement = select(SingleVideoDetails).where(
        SingleVideoDetails.video_id == video_id,
        SingleVideoDetails.user_id == current_user.id
    )
    transcript = db.exec(statement).first()
    if not transcript:
        raise Exception("Video transcript not found or not generated yet", video_id=str(video_id), user_id=str(current_user.id))
    result = await generate_video_thumbnail(video_id, str(transcript), current_user.id, db)
    
    # Map the result to ThumbnailUpdateResponse format
    from .model import ThumbnailUpdateResponse
    return ThumbnailUpdateResponse(
        success=result.get("success", False),
        message=result.get("message", "Thumbnail generation completed"),
        video_id=video_id,
        thumbnail_url=result.get("image_url"),  # Map image_url to thumbnail_url
        method_used="ai_generation"
    )

# select generated thumbnail and update 
@router.post("/{video_id}/select-generated-thumbnail-and-update", response_model=ThumbnailUpdateResponse)
async def select_generated_thumbnail_endpoint(
    video_id: str,
    url:str,
    dir_path: str = "thumbnails",
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Select a generated thumbnail and update the database
    """
    return await select_generated_thumbnail_controller(video_id, url, current_user.id, db, dir_path)


# upload custom thumbnail
@router.post("/{video_id}/upload-custom-thumbnail", response_model=ThumbnailUpdateResponse)
async def upload_custom_thumbnail_endpoint(
    video_id: str,
    file: UploadFile = File(...),
    dir_path: str = "thumbnails",
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Upload a custom thumbnail for a video
    """
    return await upload_custom_thumbnail_controller(video_id=video_id, file=file, user_id=current_user.id, dir_path=dir_path, db=db)   


# update thumbnail
@router.post("/{video_id}/update-thumbnail", response_model=ThumbnailUpdateResponse)
async def update_thumbnail_endpoint(
    video_id: str,
    url:str,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Update a thumbnail for a video
    """
    return await update_thumbnail_controller(video_id, url, current_user.id, db)