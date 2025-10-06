from typing import Dict, Any
from uuid import UUID
from sqlmodel import Session

from .service import set_video_privacy_status, get_video_privacy_status
from .model import PrivacyStatusRequest
from ....utils.my_logger import get_logger

logger = get_logger("PRIVACY_STATUS_CONTROLLER")


def set_privacy_status_controller(video_id: UUID, user_id: UUID, privacy_data: PrivacyStatusRequest, db: Session) -> Dict[str, Any]:
    """
    Set privacy status for a user's video - HTTP layer only
    """
    return set_video_privacy_status(video_id, user_id, privacy_data, db)


def get_privacy_status_controller(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Get privacy status for a user's video - HTTP layer only
    """
    return get_video_privacy_status(video_id, user_id, db)