from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, BackgroundTasks
from sqlmodel import Session
from typing import List
from uuid import UUID
from .controller import (
    upload_video_controller,
    get_user_videos_controller,
    get_video_by_id_controller,
    download_and_store_video_controller,
    update_video_controller,
    VideoControllerResponse
)
from .model import VideoResponse, VideoUpdate
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp
from ..helpers.video_cleanup_utility import video_cleanup_service

router = APIRouter(prefix="/videos", tags=["Video"])

@router.post("/upload", response_model=VideoControllerResponse)
async def upload_video_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Upload a video file for the authenticated user
    """
    return await upload_video_controller(file, current_user.id, db, background_tasks)

# @router.post("/download", response_model=VideoControllerResponse)
# async def download_video_endpoint(
#     background_tasks: BackgroundTasks,
#     video_url: str = Form(...),
#     current_user: UserSignUp = Depends(get_current_user),
#     db: Session = Depends(get_database_session)
# ):
#     """
#     Download a video from URL and store for the authenticated user
#     """
#     return await download_and_store_video_controller(video_url, current_user.id, db, background_tasks)

@router.get("/my-videos", response_model=VideoControllerResponse)
async def get_my_videos(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get all videos for the authenticated user
    """
    return get_user_videos_controller(current_user.id, db)

@router.get("/{video_id}", response_model=VideoControllerResponse)
async def get_my_video(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get a specific video by ID for the authenticated user
    """
    return get_video_by_id_controller(video_id, current_user.id, db)

@router.put("/{video_id}", response_model=VideoControllerResponse)
async def update_my_video(
    video_id: UUID,
    video_update: VideoUpdate,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Update a specific video by ID for the authenticated user
    """
    return update_video_controller(video_id, current_user.id, video_update, db)

@router.post("/{video_id}/cancel-cleanup")
async def cancel_video_cleanup(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Cancel scheduled cleanup for a video
    """
    # Verify video belongs to user
    video_result = get_video_by_id_controller(video_id, current_user.id, db)
    
    # Cancel cleanup
    video_cleanup_service.cancel_cleanup(video_id)
    
    return {"message": f"Cleanup cancelled for video {video_id}"}

@router.get("/debug/active-cleanups")
async def get_active_cleanups(
    current_user: UserSignUp = Depends(get_current_user)
):
    """
    Get list of active cleanup tasks (for debugging)
    """
    
    active_cleanups = video_cleanup_service.get_active_cleanups()
    return {"active_cleanups": active_cleanups} 