"""
All-in-one video processing controller
"""
from uuid import UUID
from sqlmodel import Session

from .service import process_video_all_in_one, save_generated_content
from .model import AllInOneRequest, AllInOneResponse, SaveContentRequest, SaveContentResponse
from ....utils.my_logger import get_logger

logger = get_logger("ALL_IN_ONE_CONTROLLER")


async def process_video_all_in_one_controller(
    video_id: str,
    user_id: UUID,
    db: Session
) -> AllInOneResponse:
    """Process video with all available generation features"""
    # Create request object with video_id for service
    request = AllInOneRequest()
    request.video_id = video_id
    return await process_video_all_in_one(request, user_id, db)


async def save_generated_content_controller(
    request: SaveContentRequest,
    video_id: str,
    user_id: UUID,
    db: Session
) -> SaveContentResponse:
    """Save selected generated content to video record"""
    return await save_generated_content(request, video_id, user_id, db)
