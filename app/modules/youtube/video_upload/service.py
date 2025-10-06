"""
Service layer for video upload management
"""
import os
from typing import Optional, Dict, Any
from uuid import UUID
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from sqlmodel import Session, select

from ..video.model import Video
from ..youtube_creds.controller import get_youtube_credentials_controller
from .error_models import (
    VideoUploadError,
    VideoFileNotFoundError,
    InvalidVideoFormatError,
    UploadInterruptedError,
    ThumbnailUploadError,
    PlaylistAdditionError,
    VideoMetadataError,
    YouTubeApiQuotaError,
    VideoTooLargeError,
    UploadTimeoutError,
    YouTubeApiError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger
from ..helpers.youtube_client import get_youtube_client

logger = get_logger("YOUTUBE_UPLOAD_SERVICE")

# Constants
MAX_VIDEO_SIZE = 128 * 1024 * 1024 * 1024  # 128GB (YouTube limit)
SUPPORTED_FORMATS = ['.mp4', '.mov', '.avi', '.wmv', '.flv', '.webm', '.mkv']
UPLOAD_TIMEOUT = 3600  # 1 hour


def upload_video_to_youtube_service(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Upload a video to YouTube with all data from database.
    
    Args:
        video_id: UUID of the video to upload
        user_id: UUID of the user
        db: Database session
        
    Returns:
        Dict containing upload result
    """
    try:
        logger.info(f"Starting YouTube upload for video {video_id}, user {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise YouTubeApiError("Failed to get YouTube client for user", user_id=str(user_id))
        
        # Get video from database
        video = _get_video_from_database(video_id, user_id, db)
        
        # Validate video file
        _validate_video_file(video)
        
        # Determine upload privacy status
        upload_privacy_status = _determine_privacy_status(video)
        
        # Prepare video metadata
        body = _prepare_video_metadata(video, upload_privacy_status)
        
        # Create media upload object
        media = _create_media_upload(video)
        
        logger.info(f"Uploading video: {video.title} ({upload_privacy_status})")
        
        # Upload video
        youtube_video_id = _upload_video_to_youtube(youtube, body, media)
        
        # Upload thumbnail if available
        thumbnail_result = _upload_thumbnail_if_available(youtube, youtube_video_id, video)
        
        # Update database
        _update_video_in_database(video, youtube_video_id, db)
        
        # Add to playlist if specified
        playlist_result = _add_to_playlist_if_specified(youtube, youtube_video_id, video)
        
        # Prepare response
        result = _prepare_upload_response(video, youtube_video_id, upload_privacy_status, playlist_result, thumbnail_result)
        
        logger.info(f"YouTube upload completed for video {video_id}")
        return result
        
    except Exception as e:
        if isinstance(e, (VideoUploadError, VideoFileNotFoundError, InvalidVideoFormatError, 
                         UploadInterruptedError, ThumbnailUploadError, PlaylistAdditionError,
                         VideoMetadataError, YouTubeApiQuotaError, VideoTooLargeError,
                         UploadTimeoutError, YouTubeApiError, ValidationError, DatabaseError)):
            raise
        raise VideoUploadError(f"Unexpected error during video upload: {str(e)}", 
                              video_id=str(video_id), user_id=str(user_id))


def _get_video_from_database(video_id: UUID, user_id: UUID, db: Session) -> Video:
    """Get video from database with validation"""
    # Database operations
    try:
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            raise ValidationError("Video not found in database", field="video_id", 
                                value=str(video_id), error_type="video_not_found")
        
        logger.info(f"Video found in database: {video.title}")
        return video
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise DatabaseError(f"Error retrieving video from database: {str(e)}", 
                          operation="select_video", error_type="query")


def _validate_video_file(video: Video) -> None:
    """Validate video file exists and is in supported format"""
    if not os.path.exists(video.video_path):
        raise VideoFileNotFoundError("Video file not found on disk", 
                                   video_id=str(video.id), file_path=video.video_path)
    
    # Check file format
    file_extension = os.path.splitext(video.video_path)[1].lower()
    if file_extension not in SUPPORTED_FORMATS:
        raise InvalidVideoFormatError("Unsupported video format", 
                                    video_id=str(video.id), file_format=file_extension)
    
    # Check file size
    file_size = os.path.getsize(video.video_path)
    if file_size > MAX_VIDEO_SIZE:
        raise VideoTooLargeError("Video file too large", 
                               video_id=str(video.id), file_size=file_size, max_size=MAX_VIDEO_SIZE)
    
    logger.info(f"Video file validation passed: {video.video_path}")


def _determine_privacy_status(video: Video) -> str:
    """Determine the privacy status for upload"""
    if video.schedule_datetime:
        return 'private'  # Always private when scheduling
    else:
        return video.privacy_status or 'private'


def _prepare_video_metadata(video: Video, privacy_status: str) -> Dict[str, Any]:
    """Prepare video metadata for YouTube upload"""
    if not video.title:
        raise VideoMetadataError("Video title is required", video_id=str(video.id), field="title")
    
    body = {
        'snippet': {
            'title': video.title,
            'description': video.description or '',
            'tags': ['auto-generated', 'transcript-based'],
            'categoryId': '22'  # People & Blogs
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Add scheduling if provided
    if video.schedule_datetime:
        body['status']['publishAt'] = video.schedule_datetime
    
    logger.info(f"Video metadata prepared: {video.title}")
    return body


def _create_media_upload(video: Video) -> MediaFileUpload:
    """Create media upload object"""
    try:
        media = MediaFileUpload(
            video.video_path,
            chunksize=-1,
            resumable=True,
            mimetype='video/mp4'
        )
        logger.info(f"Media upload object created for: {video.video_path}")
        return media
    except Exception as e:
        raise VideoUploadError(f"Failed to create media upload object: {str(e)}", 
                              video_id=str(video.id))


def _upload_video_to_youtube(youtube, body: Dict[str, Any], media: MediaFileUpload) -> str:
    """Upload video to YouTube and return video ID"""
    try:
        upload_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media,
        )
        
        # Monitor upload progress
        response = None
        while response is None:
            status, response = upload_request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"Upload progress: {progress}%")
        
        youtube_video_id = response['id']
        logger.info(f"Video uploaded successfully! YouTube ID: {youtube_video_id}")
        return youtube_video_id
        
    except HttpError as e:
        if e.resp.status == 403:
            raise YouTubeApiQuotaError("YouTube API quota exceeded", user_id="unknown")
        elif e.resp.status == 401:
            raise YouTubeApiError("YouTube API authentication failed", api_endpoint="videos.insert")
        else:
            raise YouTubeApiError(f"YouTube API error: {str(e)}", api_endpoint="videos.insert")
    except Exception as e:
        raise UploadInterruptedError(f"Upload interrupted: {str(e)}")


def _upload_thumbnail_if_available(youtube, youtube_video_id: str, video: Video) -> Dict[str, Any]:
    """Upload thumbnail if available"""
    if not video.thumbnail_path:
        logger.info("No thumbnail available for upload")
        return {
            'success': False,
            'message': 'No thumbnail available'
        }
    
    if not os.path.exists(video.thumbnail_path):
        logger.warning(f"Thumbnail file not found: {video.thumbnail_path}")
        return {
            'success': False,
            'error': 'Thumbnail file not found',
            'message': 'Thumbnail file not found on disk'
        }
    
    try:
        logger.info(f"Uploading thumbnail: {video.thumbnail_path}")
        
        youtube.thumbnails().set(
            videoId=youtube_video_id,
            media_body=MediaFileUpload(video.thumbnail_path, mimetype='image/jpeg')
        ).execute()
        
        logger.info(f"Thumbnail uploaded successfully for video {youtube_video_id}")
        return {
            'success': True,
            'thumbnail_path': video.thumbnail_path,
            'message': 'Thumbnail uploaded successfully'
        }
        
    except HttpError as e:
        raise ThumbnailUploadError(f"Error uploading thumbnail: {str(e)}", 
                                 video_id=str(video.id), youtube_video_id=youtube_video_id,
                                 thumbnail_path=video.thumbnail_path)
    except Exception as e:
        raise ThumbnailUploadError(f"Unexpected error uploading thumbnail: {str(e)}", 
                                 video_id=str(video.id), youtube_video_id=youtube_video_id,
                                 thumbnail_path=video.thumbnail_path)


def _update_video_in_database(video: Video, youtube_video_id: str, db: Session) -> None:
    """Update video in database with YouTube video ID"""
    # Database operations
    try:
        video.youtube_video_id = youtube_video_id
        video.video_status = 'uploaded'
        db.add(video)
        db.commit()
        db.refresh(video)
        
        logger.info(f"Video updated in database with YouTube ID: {youtube_video_id}")
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error updating video in database: {str(e)}", 
                          operation="update_video", error_type="transaction")


def _add_to_playlist_if_specified(youtube, youtube_video_id: str, video: Video) -> Dict[str, Any]:
    """Add video to playlist if playlist name is specified"""
    if not video.playlist_name:
        logger.info("No playlist selected for this video")
        return {
            'success': False,
            'message': 'No playlist selected'
        }
    
    try:
        # Get user's playlists
        playlists_response = youtube.playlists().list(
            part='snippet',
            mine=True,
            maxResults=50
        ).execute()
        
        # Find or create playlist
        playlist_id = _find_or_create_playlist(youtube, playlists_response, video.playlist_name)
        
        # Add video to playlist
        youtube.playlistItems().insert(
            part='snippet',
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': youtube_video_id
                    }
                }
            }
        ).execute()
        
        logger.info(f"Video added to playlist: {video.playlist_name}")
        return {
            'playlist_name': video.playlist_name,
            'playlist_id': playlist_id,
            'success': True
        }
        
    except HttpError as e:
        raise PlaylistAdditionError(f"Error adding to playlist: {str(e)}", 
                                  video_id=str(video.id), youtube_video_id=youtube_video_id,
                                  playlist_name=video.playlist_name)
    except Exception as e:
        raise PlaylistAdditionError(f"Unexpected error adding to playlist: {str(e)}", 
                                  video_id=str(video.id), youtube_video_id=youtube_video_id,
                                  playlist_name=video.playlist_name)


def _find_or_create_playlist(youtube, playlists_response: Dict[str, Any], playlist_name: str) -> str:
    """Find existing playlist or create new one"""
    # Find existing playlist
    for playlist in playlists_response.get('items', []):
        if playlist['snippet']['title'].lower() == playlist_name.lower():
            return playlist['id']
    
    # Create new playlist
    playlist_body = {
        'snippet': {
            'title': playlist_name,
            'description': f'Playlist created by {playlist_name}'
        },
        'status': {
            'privacyStatus': 'private'
        }
    }
    playlist_response = youtube.playlists().insert(
        part='snippet,status',
        body=playlist_body
    ).execute()
    
    return playlist_response['id']


def _prepare_upload_response(video: Video, youtube_video_id: str, privacy_status: str, 
                           playlist_result: Dict[str, Any], thumbnail_result: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare the final upload response"""
    result = {
        'success': True,
        'youtube_video_id': youtube_video_id,
        'video_title': video.title,
        'privacy_status': privacy_status,
        'schedule_datetime': video.schedule_datetime,
        'youtube_url': f"https://www.youtube.com/watch?v={youtube_video_id}",
        'playlist_result': playlist_result,
        'thumbnail_result': thumbnail_result
    }
    
    if video.schedule_datetime:
        result['message'] = f"Video uploaded and scheduled for {video.schedule_datetime}"
    else:
        result['message'] = "Video uploaded successfully"
    
    return result