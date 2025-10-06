"""
Controller layer for playlist operations
"""
from typing import Dict, Any
from uuid import UUID
from sqlmodel import Session

from .service import get_user_playlists_service, get_playlist_details_service, get_playlist_all_videos_service
from .model import PlaylistControllerResponse, PlaylistDetailsControllerResponse, PlaylistDetailsResponse, PlaylistAllVideosControllerResponse, PlaylistAllVideosResponse
from ....utils.my_logger import get_logger

logger = get_logger("PLAYLIST_CONTROLLER")


def get_user_playlists_controller(user_id: UUID, db: Session, refresh: bool = False) -> PlaylistControllerResponse:
    """Get all playlists for a specific user"""
    result = get_user_playlists_service(user_id, db, refresh)
    
    return PlaylistControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("playlists_data", {}),
        refreshed=result.get("refreshed", False)
    )


def get_playlist_details_controller(user_id: UUID, playlist_id: str, db: Session, refresh: bool = False) -> PlaylistDetailsControllerResponse:
    """Get detailed information about a specific playlist"""
    result = get_playlist_details_service(user_id, playlist_id, db, refresh)
    
    playlist_data = None
    if result.get("data"):
        playlist_data = PlaylistDetailsResponse(**result["data"])
    
    return PlaylistDetailsControllerResponse(
        success=result["success"],
        message=result["message"],
        data=playlist_data
    )


def get_playlist_all_videos_controller(user_id: UUID, playlist_id: str, db: Session, refresh: bool = False) -> PlaylistAllVideosControllerResponse:
    """Get all videos from a specific playlist"""
    result = get_playlist_all_videos_service(user_id, playlist_id, db, refresh)
    
    playlist_data = None
    if result.get("data"):
        playlist_data = PlaylistAllVideosResponse(**result["data"])
    
    return PlaylistAllVideosControllerResponse(
        success=result["success"],
        message=result["message"],
        data=playlist_data
    )