from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Path, Body, Query
from sqlmodel import Session
from pydantic import BaseModel

from .controller import (
    get_playlists_controller,
    create_playlist_controller,
    get_playlist_videos_controller,
    select_playlist_controller,
    get_video_playlist_controller
)
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp
from .model import PlaylistCreateRequest, PlaylistResponse, PlaylistCreateResponse
from ....utils.my_logger import get_logger

logger = get_logger("PLAYLIST_ROUTES")

router = APIRouter(prefix="/playlists", tags=["Playlist"])

# Request/Response models for playlist selection
class PlaylistSelectionResponse(BaseModel):
    """Response model for playlist selection operations"""
    success: bool
    message: str
    data: Dict[str, Any]

class PlaylistBasicInfo(BaseModel):
    """Basic playlist information with only name and ID"""
    id: str
    name: str

# @router.get("/my-playlists")
# async def get_my_playlists(
#     current_user: UserSignUp = Depends(get_current_user),
#     db: Session = Depends(get_database_session)
# ) -> Dict[str, Any]:
#     """
#     Get all playlists for the authenticated user.
    
#     Args:
#         current_user: The authenticated user from JWT token
#         db: Database session dependency
    
#     Returns:
#         Dict[str, Any]: Response with success status, message, data, and count
#     """
#     logger.info(f"Playlist request received for user_id: {current_user.id}")
#     result = get_playlists_controller(current_user.id, db)
    
#     return {
#         "success": result["success"],
#         "message": result["message"],
#         "data": result["playlists"],
#         "count": result["count"]
#     }

@router.post("/create", response_model=Dict[str, Any])
async def create_playlist(
    playlist_data: PlaylistCreateRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Create a new playlist for the authenticated user.
    
    Args:
        playlist_data: PlaylistCreateRequest containing playlist_name and optional description
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        Dict[str, Any]: Playlist creation response with success status and playlist details
    """
    logger.info(f"Create playlist request received for user_id: {current_user.id}, playlist_name: {playlist_data.playlist_name}")
    
    result = create_playlist_controller(current_user.id, playlist_data, db)
    
    return {
        "success": result["success"],
        "message": result["message"],
        "playlist_id": result["playlist_id"],
        "playlist_name": result["playlist_name"],
        "description": result["description"],
        "privacy_status": result["privacy_status"]
    }

# @router.get("/{playlist_id}/videos")
# async def get_playlist_videos(
#     playlist_id: str = Path(..., description="YouTube playlist ID"),
#     current_user: UserSignUp = Depends(get_current_user),
#     db: Session = Depends(get_database_session)
# ) -> Dict[str, Any]:
#     """
#     Get all videos from a specific playlist.
    
#     Args:
#         playlist_id: YouTube playlist ID
#         current_user: The authenticated user from JWT token
#         db: Database session dependency
    
#     Returns:
#         Dict[str, Any]: Response with success status, message, and videos list
#     """
#     logger.info(f"Get playlist videos request received for user_id: {current_user.id}, playlist_id: {playlist_id}")
    
#     result = get_playlist_videos_controller(playlist_id, current_user.id, db)
    
#     return {
#         "success": result["success"],
#         "message": result["message"],
#         "playlist_id": result["playlist_id"],
#         "videos": result["videos"],
#         "count": result["count"]
#     }

@router.post("/{video_id}/select", response_model=PlaylistSelectionResponse)
async def select_playlist_for_video(
    video_id: UUID = Path(..., description="The ID of the video"),
    playlist_name: str = Body(..., description="Name of the playlist to select"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> PlaylistSelectionResponse:
    """
    Select a playlist for a video (create if doesn't exist).
    
    Args:
        video_id: The UUID of the video
        playlist_name: Name of the playlist to select
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        PlaylistSelectionResponse: Playlist selection response
    """
    logger.info(f"Select playlist request received for video_id: {video_id}, user_id: {current_user.id}, playlist_name: {playlist_name}")
    
    result = select_playlist_controller(video_id, current_user.id, playlist_name, db)
    
    return PlaylistSelectionResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )

# @router.get("/{video_id}/selected")
# async def get_video_playlist(
#     video_id: UUID = Path(..., description="The ID of the video"),
#     current_user: UserSignUp = Depends(get_current_user),
#     db: Session = Depends(get_database_session)
# ) -> Dict[str, Any]:
#     """
#     Get the selected playlist for a video.
    
#     Args:
#         video_id: The UUID of the video
#         current_user: The authenticated user from JWT token
#         db: Database session dependency
    
#     Returns:
#         Dict[str, Any]: Response with playlist information
#     """
#     logger.info(f"Get video playlist request received for video_id: {video_id}, user_id: {current_user.id}")
    
#     result = get_video_playlist_controller(video_id, current_user.id, db)
    
#     return {
#         "success": result["success"],
#         "message": result["message"],
#         "playlist_name": result["playlist_name"],
#         "playlist_id": result["playlist_id"],
#         "video_id": result["video_id"],
#         "playlist_exists": result["playlist_exists"]
#     }