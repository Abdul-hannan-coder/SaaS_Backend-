from typing import List, Dict, Any, Optional
from uuid import UUID
from googleapiclient.errors import HttpError
from sqlmodel import Session, select
from ..video.model import Video
from ..helpers.youtube_client import get_youtube_client
from .error_models import (
    PlaylistCreationError,
    PlaylistRetrievalError,
    PlaylistSelectionError,
    VideoNotFoundError,
    VideoAccessDeniedError,
    YouTubeApiError,
    YouTubeAuthError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger

logger = get_logger("PLAYLIST_SERVICE")

# Default values for playlist creation
DEFAULT_PLAYLIST_DESCRIPTION = "Playlist created by {name}"
DEFAULT_PRIVACY_STATUS = "private"

# Core service functions with proper error handling

def get_user_playlists_service(user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Get all playlists for a user from YouTube API
    """
    # Get YouTube client
    youtube = get_youtube_client(user_id, db)
    if not youtube:
        raise YouTubeAuthError("Failed to authenticate with YouTube API", user_id=str(user_id))
    
    try:
        playlists = _get_user_playlists(youtube)
        
        logger.info(f"Successfully retrieved {len(playlists)} playlists for user {user_id}")
        
        return {
            "success": True,
            "message": f"Retrieved {len(playlists)} playlists successfully",
            "playlists": playlists,
            "count": len(playlists)
        }
        
    except HttpError as e:
        raise YouTubeApiError(f"YouTube API error: {str(e)}", api_error_code=str(e.resp.status))
    except Exception as e:
        raise PlaylistRetrievalError(f"Error retrieving playlists: {str(e)}", user_id=str(user_id))


def create_playlist_service(user_id: UUID, playlist_name: str, description: str = "", privacy_status: str = "private", db: Session = None) -> Dict[str, Any]:
    """
    Create a new playlist for a user
    """
    # Validate playlist name
    if not playlist_name or not playlist_name.strip():
        raise ValidationError("Playlist name is required", field="playlist_name", error_type="missing_field")
    
    if len(playlist_name.strip()) < 1:
        raise ValidationError("Playlist name must be at least 1 character long", field="playlist_name", error_type="too_short")
    
    if len(playlist_name.strip()) > 150:
        raise ValidationError("Playlist name must be less than 150 characters", field="playlist_name", error_type="too_long")
    
    # Get YouTube client
    youtube = get_youtube_client(user_id, db)
    if not youtube:
        raise YouTubeAuthError("Failed to authenticate with YouTube API", user_id=str(user_id))
    
    try:
        playlist_id = _create_new_playlist(youtube, playlist_name.strip(), description.strip(), privacy_status)
        
        logger.info(f"Successfully created playlist '{playlist_name}' for user {user_id}")
        
        return {
            "success": True,
            "message": "Playlist created successfully",
            "playlist_id": playlist_id,
            "playlist_name": playlist_name.strip(),
            "description": description.strip(),
            "privacy_status": privacy_status
        }
        
    except HttpError as e:
        raise YouTubeApiError(f"YouTube API error creating playlist: {str(e)}", api_error_code=str(e.resp.status))
    except Exception as e:
        raise PlaylistCreationError(f"Error creating playlist: {str(e)}", user_id=str(user_id), playlist_name=playlist_name)


def select_playlist_for_video_service(video_id: UUID, user_id: UUID, playlist_name: str, db: Session) -> Dict[str, Any]:
    """
    Select a playlist for a video (create if doesn't exist)
    """
    # Validate playlist name
    if not playlist_name or not playlist_name.strip():
        raise ValidationError("Playlist name is required", field="playlist_name", error_type="missing_field")
    
    # Check if video exists and user has access
    statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found or you don't have permission to update it", video_id=str(video_id), user_id=str(user_id))
    
    # Get YouTube client
    youtube = get_youtube_client(user_id, db)
    if not youtube:
        raise YouTubeAuthError("Failed to authenticate with YouTube API", user_id=str(user_id))
    
    try:
        # Get user's playlists
        playlists = _get_user_playlists(youtube)
        
        # Find existing playlist or create new one
        playlist_id = None
        playlist_exists = False
        
        for playlist in playlists:
            if playlist['title'].lower() == playlist_name.strip().lower():
                playlist_id = playlist['id']
                playlist_exists = True
                break
        
        if not playlist_id:
            # Create new playlist
            playlist_id = _create_new_playlist(youtube, playlist_name.strip())
            logger.info(f"Created new playlist: {playlist_name}")
        
        # Database operations
        try:
            # Save playlist name to video model
            video.playlist_name = playlist_name.strip()
            db.add(video)
            db.commit()
            db.refresh(video)
            
            logger.info(f"Successfully saved playlist '{playlist_name}' for video {video_id}")
            
            return {
                "success": True,
                "message": f"Playlist '{playlist_name}' {'selected' if playlist_exists else 'created and selected'} for video",
                "playlist_name": playlist_name.strip(),
                "playlist_id": playlist_id,
                "playlist_exists": playlist_exists,
                "video_id": str(video_id)
            }
            
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Error saving playlist to video: {str(e)}", operation="select_playlist_for_video", error_type="transaction")
        
    except HttpError as e:
        raise YouTubeApiError(f"YouTube API error: {str(e)}", api_error_code=str(e.resp.status))
    except Exception as e:
        raise PlaylistSelectionError(f"Error selecting playlist: {str(e)}", video_id=str(video_id), user_id=str(user_id), playlist_name=playlist_name)


def get_video_playlist_service(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Get the selected playlist for a video
    """
    # Check if video exists and user has access
    statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found or you don't have permission to access it", video_id=str(video_id), user_id=str(user_id))
    
    if not video.playlist_name:
        return {
            "success": True,
            "message": "No playlist selected for this video",
            "playlist_name": None,
            "playlist_id": None,
            "video_id": str(video_id),
            "playlist_exists": False
        }
    
    # Get YouTube client to verify playlist still exists
    youtube = get_youtube_client(user_id, db)
    if not youtube:
        raise YouTubeAuthError("Failed to authenticate with YouTube API", user_id=str(user_id))
    
    try:
        # Get user's playlists to find the playlist ID
        playlists = _get_user_playlists(youtube)
        playlist_id = None
        
        for playlist in playlists:
            if playlist['title'].lower() == video.playlist_name.lower():
                playlist_id = playlist['id']
                break
        
        logger.info(f"Successfully retrieved playlist info for video {video_id}")
        
        return {
            "success": True,
            "message": "Playlist information retrieved successfully",
            "playlist_name": video.playlist_name,
            "playlist_id": playlist_id,
            "video_id": str(video_id),
            "playlist_exists": playlist_id is not None
        }
        
    except HttpError as e:
        raise YouTubeApiError(f"YouTube API error: {str(e)}", api_error_code=str(e.resp.status))
    except Exception as e:
        raise PlaylistRetrievalError(f"Error getting playlist for video: {str(e)}", user_id=str(user_id))


def get_playlist_videos_service(playlist_id: str, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Get videos from a specific playlist
    """
    # Validate playlist ID
    if not playlist_id or not playlist_id.strip():
        raise ValidationError("Playlist ID is required", field="playlist_id", error_type="missing_field")
    
    # Get YouTube client
    youtube = get_youtube_client(user_id, db)
    if not youtube:
        raise YouTubeAuthError("Failed to authenticate with YouTube API", user_id=str(user_id))
    
    try:
        videos = _get_playlist_videos_by_id(youtube, playlist_id.strip())
        
        logger.info(f"Successfully retrieved {len(videos)} videos from playlist {playlist_id}")
        
        return {
            "success": True,
            "message": f"Retrieved {len(videos)} videos from playlist",
            "playlist_id": playlist_id.strip(),
            "videos": videos,
            "count": len(videos)
        }
        
    except HttpError as e:
        raise YouTubeApiError(f"YouTube API error: {str(e)}", api_error_code=str(e.resp.status))
    except Exception as e:
        raise PlaylistRetrievalError(f"Error getting playlist videos: {str(e)}", user_id=str(user_id)) 








# ======================================
# ======================================

# Helper functions


# ======================================
# ======================================




def _get_playlists_response(youtube):
    """
    Helper function to get playlists response from YouTube API.
    
    Args:
        youtube: Authenticated YouTube API client
    
    Returns:
        dict: YouTube API response for playlists
    """
    return youtube.playlists().list(
        part='snippet',
        mine=True,
        maxResults=50
    ).execute()

def _get_user_playlists(youtube):
    """
    Get all playlists from the user's channel.
    
    Args:
        youtube: Authenticated YouTube API client
    
    Returns:
        list: List of playlist dictionaries with id, title, and description
    """
    try:
        playlists_response = _get_playlists_response(youtube)
        
        playlists = []
        for playlist in playlists_response.get('items', []):
            playlists.append({
                'id': playlist['id'],
                'title': playlist['snippet']['title'],
                'description': playlist['snippet'].get('description', ''),
                'privacy': playlist['snippet'].get('privacyStatus', 'private')
            })
        
        logger.info(f"Successfully fetched {len(playlists)} playlists")
        return playlists
        
    except HttpError as e:
        logger.error(f"❌ Error fetching playlists: {e}")
        return []

def _create_new_playlist(youtube, playlist_name, description="", privacy_status="private"):
    """
    Create a new playlist.
    
    Args:
        youtube: Authenticated YouTube API client
        playlist_name (str): Name of the playlist
        description (str): Description for the playlist
        privacy_status (str): Privacy status of the playlist (private, public, unlisted)
    
    Returns:
        str: Playlist ID
    """
    try:
        return _execute_playlist_creation(youtube, playlist_name, description, privacy_status)
    except HttpError as e:
        logger.error(f"❌ Error creating playlist: {e}")
        raise



def _create_playlist_body(title, description="", privacy_status="private"):
    """
    Helper function to create playlist request body.
    
    Args:
        title (str): Playlist title
        description (str): Playlist description
        privacy_status (str): Privacy status of the playlist
    
    Returns:
        dict: Playlist request body
    """
    return {
        'snippet': {
            'title': title,
            'description': description or DEFAULT_PLAYLIST_DESCRIPTION.format(name=title)
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

def _execute_playlist_creation(youtube, title, description="", privacy_status="private"):
    """
    Helper function to execute playlist creation.
    
    Args:
        youtube: Authenticated YouTube API client
        title (str): Playlist title
        description (str): Playlist description
        privacy_status (str): Privacy status of the playlist
    
    Returns:
        str: Playlist ID
    """
    playlist_response = youtube.playlists().insert(
        part='snippet,status',
        body=_create_playlist_body(title, description, privacy_status)
    ).execute()
    
    playlist_id = playlist_response['id']
    logger.info(f"✅ Created new playlist: {title} with ID: {playlist_id} and privacy: {privacy_status}")
    return playlist_id

def _get_playlist_videos_by_id(youtube, playlist_id: str) -> List[Dict[str, Any]]:
    """
    Get videos from a specific playlist using playlist ID.
    
    Args:
        youtube: Authenticated YouTube API client
        playlist_id: YouTube playlist ID
    
    Returns:
        List[Dict[str, Any]]: List of videos with their details
    """
    try:
        # Get playlist items
        request = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=playlist_id,
            maxResults=50
        )
        
        videos = []
        while request:
            response = request.execute()
            
            for item in response['items']:
                video_id = item['contentDetails']['videoId']
                snippet = item['snippet']
                
                # Get additional video details
                video_details = _get_video_details(youtube, video_id)
                
                # Get only medium thumbnail (most commonly used)
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = thumbnails.get('medium', {}).get('url', '') if thumbnails else ''
                
                video_data = {
                    'title': snippet['title'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'video_id': video_id,
                    'published_at': snippet['publishedAt'],
                    'description': snippet.get('description', ''),
                    'thumbnail_url': thumbnail_url,
                    'position': snippet.get('position', 0)
                }
                
                # Add video details if available
                if video_details:
                    video_data.update({
                        'view_count': video_details.get('viewCount', 'N/A'),
                        'like_count': video_details.get('likeCount', 'N/A'),
                        'comment_count': video_details.get('commentCount', 'N/A'),
                        'duration': video_details.get('duration', 'N/A'),
                        'privacy_status': video_details.get('status', 'N/A')
                    })
                
                videos.append(video_data)
            
            request = youtube.playlistItems().list_next(request, response)
        
        logger.info(f"Successfully fetched {len(videos)} videos from playlist ID: {playlist_id}")
        return videos
        
    except HttpError as e:
        logger.error(f"❌ Error fetching playlist videos from YouTube API: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error fetching playlist videos: {e}")
        return []

def _get_video_details(youtube, video_id: str) -> Optional[Dict[str, Any]]:
    """
    Get additional details for a specific video.
    
    Args:
        youtube: Authenticated YouTube API client
        video_id: YouTube video ID
    
    Returns:
        Optional[Dict[str, Any]]: Video details or None if error
    """
    try:
        request = youtube.videos().list(
            part='statistics,contentDetails,status',
            id=video_id
        )
        response = request.execute()
        
        if response['items']:
            video = response['items'][0]
            return {
                'viewCount': video['statistics'].get('viewCount', 'N/A'),
                'likeCount': video['statistics'].get('likeCount', 'N/A'),
                'commentCount': video['statistics'].get('commentCount', 'N/A'),
                'duration': video['contentDetails'].get('duration', 'N/A'),
                'status': video['status'].get('privacyStatus', 'N/A')
            }
        return None
        
    except Exception as e:
        logger.error(f"Error getting video details for video ID {video_id}: {e}")
        return None

