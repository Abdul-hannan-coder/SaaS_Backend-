from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel, Field, validator

from .controller import (
    generate_thumbnail_for_video_controller,
    save_video_thumbnail_controller,
    upload_custom_thumbnail_controller,
    ThumbnailResponse
)
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp

router = APIRouter(prefix="/thumbnail-generator", tags=["Thumbnail Generator"])

class ThumbnailSaveRequest(BaseModel):
    thumbnail_url: str = Field(..., min_length=10)
    
    @validator('thumbnail_url')
    def validate_thumbnail_url(cls, v):
        if not v or not v.strip():
            raise ValueError("Thumbnail URL cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Thumbnail URL must be at least 10 characters long")
        if not v.strip().startswith(('http://', 'https://')):
            raise ValueError("Thumbnail URL must be a valid HTTP/HTTPS URL")
        return v.strip()

# Route 1: Generate thumbnail from video ID
@router.post("/{video_id}/generate", response_model=ThumbnailResponse)
async def generate_thumbnail_endpoint(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Generate a thumbnail image URL for a video using its transcript
    User sends video ID → get transcript → generate thumbnail → return image URL to user
    """
    return await generate_thumbnail_for_video_controller(
        video_id=video_id,
        user_id=current_user.id,
        db=db
    )

# Route 2: Save selected thumbnail
@router.post("/{video_id}/save")
async def save_thumbnail_endpoint(
    video_id: UUID,
    request: ThumbnailSaveRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Save the selected thumbnail URL to the video record
    User likes the thumbnail → send video ID + thumbnail URL → save to database
    """
    return await save_video_thumbnail_controller(
        video_id=video_id,
        user_id=current_user.id,
        thumbnail_url=request.thumbnail_url,
        db=db
    )

# Route 3: Upload custom thumbnail
@router.post("/{video_id}/upload")
async def upload_custom_thumbnail_endpoint(
    video_id: UUID,
    file: UploadFile = File(...),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Upload a custom thumbnail image from user's computer
    User uploads image file → save to thumbnails directory → store path in database
    """
    return await upload_custom_thumbnail_controller(
        video_id=video_id,
        user_id=current_user.id,
        file=file,
        db=db
    )

# # Route 4: Get saved thumbnail
# @router.get("/{video_id}/saved")
# async def get_saved_thumbnail_endpoint(
#     video_id: UUID,
#     current_user: UserSignUp = Depends(get_current_user),
#     db: Session = Depends(get_database_session)
# ):
#     """
#     Get the saved thumbnail path for a video
#     """
#     from ..video.model import Video
#     from sqlmodel import select
    
#     video = db.exec(select(Video).where(
#         Video.id == video_id,
#         Video.user_id == current_user.id
#     )).first()
    
#     if not video:
#         raise HTTPException(status_code=404, detail="Video not found")
    
#     if not video.thumbnail_path:
#         return {
#             "has_thumbnail": False,
#             "thumbnail_path": None,
#             "thumbnail_url": None,
#             "original_url": None,
#             "message": "No thumbnail saved for this video"
#         }
    
#     # Convert file path to accessible URL
#     from pathlib import Path
#     thumbnail_filename = Path(video.thumbnail_path).name
#     local_thumbnail_url = f"/thumbnails/{thumbnail_filename}"
    
#     return {
#         "has_thumbnail": True,
#         "thumbnail_path": video.thumbnail_path,
#         "thumbnail_url": local_thumbnail_url,
#         "original_url": video.thumbnail_url,
#         "video_id": str(video_id),
#         "message": "Thumbnail found"
#     } 