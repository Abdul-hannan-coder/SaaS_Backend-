from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from .controller import get_user_playlists_controller, get_playlist_details_controller, get_playlist_all_videos_controller, PlaylistControllerResponse, PlaylistDetailsControllerResponse, PlaylistAllVideosControllerResponse
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp

router = APIRouter(prefix="/playlists", tags=["Dashboard Playlist"])


@router.get("/", response_model=PlaylistControllerResponse)
async def get_user_playlists(
    refresh: bool = False,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get all playlists for the authenticated user
    
    This endpoint retrieves playlist data for the authenticated user's YouTube channel:
    
    **Playlist Information:**
    - Playlist ID and name
    - Fetches from YouTube Data API
    - Stores/updates data in user_playlist table
    - Supports refresh functionality for fresh data
    - Efficient caching for fast subsequent requests
    
    **API Logic:**
    - If refresh=True: Always fetch fresh data from YouTube API and update database
    - If refresh=False: Return cached data from database if exists, otherwise fetch from YouTube API and save to database
    
    Args:
        refresh: If True, fetch fresh data from YouTube API and update database.
                If False, return cached data from database (faster response).
        current_user: The authenticated user from Bearer token
        db: Database session dependency
    
    Returns:
        PlaylistControllerResponse: Complete playlists data with playlist IDs and names
        
    Raises:
        HTTPException: If YouTube API authentication fails or other errors occur
    """
    try:
        return get_user_playlists_controller(current_user.id, db, refresh)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving playlists: {str(e)}"
        )


@router.get("/{playlist_id}", response_model=PlaylistDetailsControllerResponse)
async def get_playlist_details(
    playlist_id: str,
    refresh: bool = False,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get detailed information about a specific playlist with top 2 videos
    
    This endpoint retrieves comprehensive playlist data for the authenticated user:
    
    **Playlist Information:**
    - Playlist ID, name, and description
    - Thumbnail URL and video count
    - Published date and channel information
    - Privacy status
    - Top 2 videos (one by views, one by likes)
    - Comprehensive analytics data
    
    **Top Videos Information:**
    - Returns exactly 2 videos: one with highest views, one with highest likes
    - Video ID, title, and description
    - Thumbnail URL and duration
    - Published date and statistics (views, likes, comments)
    - Performance type indicator (top_by_views or top_by_likes)
    
    **Video Selection Logic:**
    - Video 1: Highest view count in the playlist
    - Video 2: Highest like count in the playlist
    - If same video has both highest views and likes, second video is second-highest by likes
    - Each video includes performance_type field indicating why it was selected
    
    **Analytics Information:**
    - Total views, likes, and comments across all videos
    - Average engagement rate (likes + comments) / views
    - Top video by views (ID, title, count)
    - Top video by likes (ID, title, count)
    - Last analytics update timestamp
    - Analytics data stored in user_playlist table for future reference
    
    **API Logic:**
    - If refresh=True: Always fetch fresh data from YouTube API and update database
    - If refresh=False: Return cached data from database if exists, otherwise fetch from YouTube API and save to database
    - Analyzes all videos in playlist to find top performers
    - Stores ALL video details in single_video_details table
    - Calculates comprehensive analytics and stores in user_playlist table
    - Returns only 2 most successful videos for focused insights
    
    Args:
        playlist_id: YouTube playlist ID (e.g., "PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p")
        refresh: If True, fetch fresh data from YouTube API and update database.
                If False, return cached data from database (faster response).
        current_user: The authenticated user from Bearer token
        db: Database session dependency
    
    Returns:
        PlaylistDetailsControllerResponse: Playlist details with exactly 2 top videos and comprehensive analytics
        
    Raises:
        HTTPException: If playlist not found, YouTube API authentication fails, or other errors occur
    """
    try:
        return get_playlist_details_controller(current_user.id, playlist_id, db, refresh)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving playlist details: {str(e)}"
        )


@router.get("/{playlist_id}/videos", response_model=PlaylistAllVideosControllerResponse)
async def get_playlist_all_videos(
    playlist_id: str,
    refresh: bool = False,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get all videos from a specific playlist
    
    This endpoint retrieves all videos from a playlist for the authenticated user:
    
    **Playlist Information:**
    - Playlist ID and name
    - Total number of videos in playlist
    - Complete list of all videos with detailed information
    
    **Video Information (for each video):**
    - Video ID, title, and description
    - Thumbnail URL and duration
    - Published date and statistics (views, likes, comments)
    - Privacy status and watch time metrics
    - YouTube video URL for direct access
    
    **API Logic:**
    - If refresh=True: Always fetch fresh data from YouTube API and update database
    - If refresh=False: Return cached data from database if exists, otherwise fetch from YouTube API and save to database
    - Handles pagination for playlists with many videos
    - Stores all video details in single_video_details table
    - Returns complete video data for comprehensive analysis
    
    **Use Cases:**
    - Building video galleries and catalogs
    - Comprehensive playlist analysis
    - Video management and organization
    - Content strategy and planning
    
    Args:
        playlist_id: YouTube playlist ID (e.g., "PLrAXtmRdnEQy6nuLMOV8u4fOqR0U4vO3p")
        refresh: If True, fetch fresh data from YouTube API and update database.
                If False, return cached data from database (faster response).
        current_user: The authenticated user from Bearer token
        db: Database session dependency
    
    Returns:
        PlaylistAllVideosControllerResponse: Complete playlist with all videos and metadata
        
    Raises:
        HTTPException: If playlist not found, YouTube API authentication fails, or other errors occur
    """
    try:
        return get_playlist_all_videos_controller(current_user.id, playlist_id, db, refresh)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving playlist videos: {str(e)}"
        )
