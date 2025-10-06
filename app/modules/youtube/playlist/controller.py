from typing import Dict, Any
from uuid import UUID
from sqlmodel import Session

from .service import (
    get_user_playlists_service,
    create_playlist_service,
    select_playlist_for_video_service,
    get_video_playlist_service,
    get_playlist_videos_service
)
from .model import PlaylistCreateRequest
from ....utils.my_logger import get_logger

logger = get_logger("PLAYLIST_CONTROLLER")


def get_playlists_controller(user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Get all playlists for a user - HTTP layer only
    """
    return get_user_playlists_service(user_id, db)


def create_playlist_controller(user_id: UUID, playlist_data: PlaylistCreateRequest, db: Session) -> Dict[str, Any]:
    """
    Create a new playlist for a user - HTTP layer only
    """
    return create_playlist_service(
        user_id=user_id,
        playlist_name=playlist_data.playlist_name,
        description=playlist_data.description or "",
        privacy_status=playlist_data.privacy_status.value if playlist_data.privacy_status else "private",
        db=db
    )


def select_playlist_controller(video_id: UUID, user_id: UUID, playlist_name: str, db: Session) -> Dict[str, Any]:
    """
    Select a playlist for a video - HTTP layer only
    """
    return select_playlist_for_video_service(video_id, user_id, playlist_name, db)


def get_video_playlist_controller(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Get the selected playlist for a video - HTTP layer only
    """
    return get_video_playlist_service(video_id, user_id, db)


def get_playlist_videos_controller(playlist_id: str, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Get videos from a specific playlist - HTTP layer only
    """
    return get_playlist_videos_service(playlist_id, user_id, db)