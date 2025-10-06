from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel
from typing import Optional

from .controller import (
    generate_description_for_video_controller,
    save_video_description_controller,
    regenerate_video_description_controller,
    DescriptionResponse
)
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp

router = APIRouter(prefix="/description-generator", tags=["Description Generator"])

# DescriptionResponse is now imported from controller

class DescriptionSaveRequest(BaseModel):
    description: str

class RegenerateWithTemplateRequest(BaseModel):
    custom_template: Optional[str] = None

# Route 1: Generate description from video ID
@router.post("/{video_id}/generate", response_model=DescriptionResponse)
async def generate_description_endpoint(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Generate description for a video using its transcript
    User sends video ID → get transcript → generate description → return to user
    """
    return await generate_description_for_video_controller(
        video_id=video_id,
        user_id=current_user.id,
        db=db
    )

# Route 2: Save description when user likes it
@router.post("/{video_id}/save")
async def save_description_endpoint(
    video_id: UUID,
    request: DescriptionSaveRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Save the generated description to the video record
    User likes the description → send video ID + description → save to database
    """
    return await save_video_description_controller(
        video_id=video_id,
        user_id=current_user.id,
        description=request.description,
        db=db
    )

# Route 3: Regenerate description with custom template
@router.post("/{video_id}/regenerate-with-template", response_model=DescriptionResponse)
async def regenerate_with_template_endpoint(
    video_id: UUID,
    request: RegenerateWithTemplateRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Regenerate description with custom template
    User wants changes → send video ID + custom template → regenerate description
    """
    return await regenerate_video_description_controller(
        video_id=video_id,
        user_id=current_user.id,
        db=db,
        custom_template=request.custom_template
    )

# Route 4: Regenerate description (simple)
@router.post("/{video_id}/regenerate", response_model=DescriptionResponse)
async def regenerate_description_endpoint(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Regenerate description for a video
    User wants new description → send video ID → regenerate description
    """
    return await regenerate_video_description_controller(
        video_id=video_id,
        user_id=current_user.id,
        db=db
    ) 