from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel

from .controller import (
    generate_timestamps_for_video_controller,
    save_video_timestamps_controller,
    regenerate_video_timestamps_controller,
    TimeStampsResponse
)
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp

router = APIRouter(prefix="/timestamps-generator", tags=["Timestamps Generator"])

class TimeStampsSaveRequest(BaseModel):
    timestamps: str

# Route 1: Generate timestamps from video ID
@router.post("/{video_id}/generate", response_model=TimeStampsResponse)
async def generate_timestamps_endpoint(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Generate timestamps for a video using its transcript
    User sends video ID → get transcript → generate timestamps → return to user
    """
    return await generate_timestamps_for_video_controller(
        video_id=video_id,
        user_id=current_user.id,
        db=db
    )

# Route 2: Save timestamps when user likes them
@router.post("/{video_id}/save")
async def save_timestamps_endpoint(
    video_id: UUID,
    request: TimeStampsSaveRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Save the generated timestamps to the video record
    User likes the timestamps → send video ID + timestamps → save to database
    """
    return await save_video_timestamps_controller(
        video_id=video_id,
        user_id=current_user.id,
        timestamps=request.timestamps,
        db=db
    )

# Route 3: Regenerate timestamps
@router.post("/{video_id}/regenerate", response_model=TimeStampsResponse)
async def regenerate_timestamps_endpoint(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Regenerate timestamps for a video
    User wants new timestamps → send video ID → regenerate timestamps
    """
    return await regenerate_video_timestamps_controller(
        video_id=video_id,
        user_id=current_user.id,
        db=db
    ) 