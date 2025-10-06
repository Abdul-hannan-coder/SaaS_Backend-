"""
Service layer for video management
"""
import shutil
from pathlib import Path
from typing import List, Dict, Any
from uuid import UUID
from fastapi import UploadFile, BackgroundTasks
from sqlmodel import Session, select

from .model import Video, VideoResponse, VideoUpdate
from .error_models import (
    VideoUploadError,
    VideoNotFoundError,
    VideoRetrievalError,
    VideoUpdateError,
    VideoDeletionError,
    VideoDownloadError,
    InvalidFileTypeError,
    FileSystemError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger
from ..helpers.video_cleanup_utility import video_cleanup_service
from ..helpers.dowload_video_url import download_youtube_video
from ..helpers.video_transcript_generator import generate_transcript_background

logger = get_logger("VIDEO_SERVICE")

# Create videos directory if it doesn't exist
VIDEOS_DIR = Path("videos")
VIDEOS_DIR.mkdir(exist_ok=True)


async def upload_video_service(
    file: UploadFile,
    user_id: UUID,
    db: Session,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Upload video file and store path in database"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith('video/'):
        raise InvalidFileTypeError("File must be a video", file_type=file.content_type)
    
    # Database operations
    try:
        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else '.mp4'
        unique_filename = f"{user_id}_{file.filename or 'video'}{file_extension}"
        file_path = VIDEOS_DIR / unique_filename
        
        # Save file to videos directory
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store video path in database
        video = Video(
            user_id=user_id,
            video_path=str(file_path)
        )
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Schedule cleanup after 30 minutes
        await video_cleanup_service.schedule_video_cleanup(video.id, str(file_path), db)
        
        # Add transcript generation to background tasks
        background_tasks.add_task(generate_transcript_background, video.id, str(file_path), db)
        
        logger.info(f"Video uploaded successfully for user {user_id}: {file_path}")
        logger.info(f"Cleanup scheduled for video {video.id} in 30 minutes")
        logger.info(f"Transcript generation scheduled in background for video {video.id}")
        
        return {
            "success": True,
            "message": "Video uploaded successfully",
            "user_id": str(user_id),
            "video": VideoResponse(
                id=video.id,
                user_id=video.user_id,
                video_path=video.video_path,
                youtube_video_id=video.youtube_video_id,
                transcript=video.transcript,
                title=video.title,
                timestamps=video.timestamps,
                description=video.description,
                thumbnail_path=video.thumbnail_path,
                thumbnail_url=video.thumbnail_url,
                privacy_status=video.privacy_status,
                schedule_datetime=video.schedule_datetime,
                video_status=video.video_status,
                playlist_name=video.playlist_name,
                created_at=video.created_at
            ).dict()
        }
        
    except Exception as e:
        db.rollback()
        if isinstance(e, (InvalidFileTypeError, FileSystemError)):
            raise
        raise DatabaseError(f"Error uploading video: {str(e)}", operation="upload_video", error_type="transaction")


def get_user_videos_service(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Get all videos for a specific user"""
    # Database operations
    try:
        statement = select(Video).where(Video.user_id == user_id)
        videos = db.exec(statement).all()
        
        video_responses = [
            VideoResponse(
                id=video.id,
                user_id=video.user_id,
                video_path=video.video_path,
                youtube_video_id=video.youtube_video_id,
                transcript=video.transcript,
                title=video.title,
                timestamps=video.timestamps,
                description=video.description,
                thumbnail_path=video.thumbnail_path,
                thumbnail_url=video.thumbnail_url,
                privacy_status=video.privacy_status,
                schedule_datetime=video.schedule_datetime,
                video_status=video.video_status,
                playlist_name=video.playlist_name,
                created_at=video.created_at
            ).dict()
            for video in videos
        ]
        
        logger.info(f"Successfully retrieved {len(video_responses)} videos for user {user_id}")
        
        return {
            "success": True,
            "message": f"Retrieved {len(video_responses)} videos",
            "user_id": str(user_id),
            "videos": video_responses,
            "count": len(video_responses)
        }
        
    except Exception as e:
        raise VideoRetrievalError(f"Error retrieving videos: {str(e)}", user_id=str(user_id))


def get_video_by_id_service(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """Get a specific video by ID for a user"""
    # Database operations
    try:
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            raise VideoNotFoundError("Video not found", video_id=str(video_id), user_id=str(user_id))
        
        logger.info(f"Successfully retrieved video {video_id} for user {user_id}")
        
        return {
            "success": True,
            "message": "Video retrieved successfully",
            "video_id": str(video_id),
            "user_id": str(user_id),
            "video": VideoResponse(
                id=video.id,
                user_id=video.user_id,
                video_path=video.video_path,
                youtube_video_id=video.youtube_video_id,
                transcript=video.transcript,
                title=video.title,
                timestamps=video.timestamps,
                description=video.description,
                thumbnail_path=video.thumbnail_path,
                thumbnail_url=video.thumbnail_url,
                privacy_status=video.privacy_status,
                schedule_datetime=video.schedule_datetime,
                video_status=video.video_status,
                playlist_name=video.playlist_name,
                created_at=video.created_at
            ).dict()
        }
        
    except Exception as e:
        if isinstance(e, VideoNotFoundError):
            raise
        raise DatabaseError(f"Error retrieving video: {str(e)}", operation="get_video_by_id", error_type="query")


async def download_and_store_video_service(
    video_url: str,
    user_id: UUID,
    db: Session,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Download video from URL and store path in database"""
    # Validate URL
    if not video_url or not video_url.strip():
        raise ValidationError("Video URL is required", field="video_url", error_type="missing_field")
    
    # Database operations
    try:
        # Download video using yt-dlp
        video_id, filepath = download_youtube_video(video_url, str(VIDEOS_DIR))
        
        if not filepath:
            raise VideoDownloadError("Failed to download video from URL", video_url=video_url, user_id=str(user_id))
        
        # Store video path in database
        video = Video(
            user_id=user_id,
            video_path=filepath,
            youtube_video_id=video_id
        )
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Schedule cleanup after 30 minutes
        await video_cleanup_service.schedule_video_cleanup(video.id, filepath, db)
        
        # Add transcript generation to background tasks
        background_tasks.add_task(generate_transcript_background, video.id, filepath, db)
        
        logger.info(f"Video downloaded and stored successfully for user {user_id}: {filepath}")
        logger.info(f"Cleanup scheduled for video {video.id} in 30 minutes")
        logger.info(f"Transcript generation scheduled in background for video {video.id}")
        
        return {
            "success": True,
            "message": "Video downloaded and stored successfully",
            "user_id": str(user_id),
            "video_url": video_url,
            "video": VideoResponse(
                id=video.id,
                user_id=video.user_id,
                video_path=video.video_path,
                youtube_video_id=video.youtube_video_id,
                transcript=video.transcript,
                title=video.title,
                timestamps=video.timestamps,
                description=video.description,
                thumbnail_path=video.thumbnail_path,
                thumbnail_url=video.thumbnail_url,
                privacy_status=video.privacy_status,
                schedule_datetime=video.schedule_datetime,
                video_status=video.video_status,
                playlist_name=video.playlist_name,
                created_at=video.created_at
            ).dict()
        }
        
    except Exception as e:
        db.rollback()
        if isinstance(e, (VideoDownloadError, ValidationError)):
            raise
        raise DatabaseError(f"Error downloading video: {str(e)}", operation="download_video", error_type="transaction")


def update_video_service(
    video_id: UUID,
    user_id: UUID,
    video_update: VideoUpdate,
    db: Session
) -> Dict[str, Any]:
    """Update a specific video by ID for a user"""
    # Database operations
    try:
        # First, get the video and verify it belongs to the user
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            raise VideoNotFoundError("Video not found", video_id=str(video_id), user_id=str(user_id))
        
        # Update only the fields that are provided in the update request
        update_data = video_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(video, field):
                setattr(video, field, value)
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        logger.info(f"Video {video_id} updated successfully for user {user_id}")
        
        return {
            "success": True,
            "message": "Video updated successfully",
            "video_id": str(video_id),
            "user_id": str(user_id),
            "video": VideoResponse(
                id=video.id,
                user_id=video.user_id,
                video_path=video.video_path,
                youtube_video_id=video.youtube_video_id,
                transcript=video.transcript,
                title=video.title,
                timestamps=video.timestamps,
                description=video.description,
                thumbnail_path=video.thumbnail_path,
                thumbnail_url=video.thumbnail_url,
                privacy_status=video.privacy_status,
                schedule_datetime=video.schedule_datetime,
                video_status=video.video_status,
                playlist_name=video.playlist_name,
                created_at=video.created_at
            ).dict()
        }
        
    except Exception as e:
        db.rollback()
        if isinstance(e, VideoNotFoundError):
            raise
        raise DatabaseError(f"Error updating video: {str(e)}", operation="update_video", error_type="transaction")
