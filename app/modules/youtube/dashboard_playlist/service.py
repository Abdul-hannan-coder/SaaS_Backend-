"""
Service layer for playlist operations
"""
from typing import Dict, Any, List,Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime

from .model import UserPlaylist, PlaylistDetailsResponse
from ..dashboard_single_video.model import SingleVideoDetails
from ....modules.youtube.helpers.youtube_client import get_youtube_client
from ....utils.my_logger import get_logger

logger = get_logger("PLAYLIST_SERVICE")


def get_user_playlists_service(user_id: UUID, db: Session, refresh: bool = False) -> Dict[str, Any]:
    """
    Get all playlists for a specific user.
    
    Logic:
    - If refresh=True: Always fetch fresh data from YouTube API and update database
    - If refresh=False: Return cached data from database if exists, otherwise fetch from YouTube API and save to database
    """
    try:
        logger.info(f"Playlist request for user_id: {user_id}, refresh: {refresh}")
        
        if refresh:
            # Case 1: User wants fresh data - always fetch from YouTube
            logger.info(f"Refresh=True: Fetching fresh playlists from YouTube API for user_id: {user_id}")
            youtube_result = _fetch_playlists_from_youtube(user_id, db)
            
            if "error" in youtube_result:
                return {
                    "success": False,
                    "message": youtube_result["error"],
                    "playlists_data": {"playlists": []},
                    "refreshed": True
                }
            
            # Save playlists to database
            saved_playlists = _save_playlists_to_database(youtube_result, user_id, db)
            message = f"Playlists refreshed from YouTube successfully. {len(saved_playlists)} playlists processed."
            logger.info(f"Successfully refreshed and saved {len(saved_playlists)} playlists for user_id: {user_id}")
            
            # Get the actual playlists list
            playlists_data = youtube_result.get("playlists", [])
            
        else:
            # Case 2: User wants cached data - return from database
            logger.info(f"Refresh=False: Returning cached playlists from database for user_id: {user_id}")
            playlists_data = _get_playlists_from_database(user_id, db)
            
            if not playlists_data:
                # Case 3: No data in database - fetch from YouTube and save
                logger.info(f"Refresh=False but no data in database: Fetching from YouTube API for user_id: {user_id}")
                youtube_result = _fetch_playlists_from_youtube(user_id, db)
                
                if "error" in youtube_result:
                    return {
                        "success": False,
                        "message": youtube_result["error"],
                        "playlists_data": {"playlists": []},
                        "refreshed": False
                    }
                
                # Save playlists to database
                saved_playlists = _save_playlists_to_database(youtube_result, user_id, db)
                message = f"Playlists fetched from YouTube and saved to database. {len(saved_playlists)} playlists processed."
                logger.info(f"Successfully fetched and saved initial {len(saved_playlists)} playlists for user_id: {user_id}")
                
                # Get the actual playlists list
                playlists_data = youtube_result.get("playlists", [])
            else:
                message = f"Playlists retrieved from database successfully. {len(playlists_data)} playlists found."
        
        return {
            "success": True,
            "message": message,
            "playlists_data": {"playlists": playlists_data},
            "refreshed": refresh
        }
        
    except Exception as e:
        logger.error(f"Error retrieving playlists for user_id {user_id}: {str(e)}")
        raise Exception(f"Error retrieving playlists: {str(e)}")


def _fetch_playlists_from_youtube(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Fetch all playlists from YouTube Data API"""
    try:
        # Get YouTube Data API client
        youtube_client = get_youtube_client(user_id, db)
        if not youtube_client:
            return {"error": "Failed to authenticate with YouTube API"}
        
        # Get all playlists for the channel
        all_playlists = []
        next_page_token = None
        
        while True:
            playlists_response = youtube_client.playlists().list(
                part='snippet,contentDetails,status',
                mine=True,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
            for playlist in playlists_response.get('items', []):
                snippet = playlist.get('snippet', {})
                content_details = playlist.get('contentDetails', {})
                status = playlist.get('status', {})
                
                playlist_data = {
                    'playlist_id': playlist['id'],
                    'playlist_name': snippet.get('title', '')
                }
                
                all_playlists.append(playlist_data)
            
            next_page_token = playlists_response.get('nextPageToken')
            if not next_page_token:
                break
        
        
        return {"playlists": all_playlists}
        
    except Exception as e:
        logger.error(f"Error fetching playlists from YouTube: {str(e)}")
        return {"error": f"Error fetching playlists from YouTube: {str(e)}"}


def _save_playlists_to_database(youtube_result: Dict[str, Any], user_id: UUID, db: Session) -> List[UserPlaylist]:
    """Save/update playlists in the database"""
    try:
        playlists_data = youtube_result.get("playlists", [])
        saved_playlists = []
        
        for playlist_data in playlists_data:
            # Check if playlist already exists
            existing_playlist = db.exec(
                select(UserPlaylist).where(
                    UserPlaylist.user_id == user_id,
                    UserPlaylist.playlist_id == playlist_data['playlist_id']
                )
            ).first()
            
            if existing_playlist:
                # Update existing record
                existing_playlist.playlist_name = playlist_data['playlist_name']
                existing_playlist.updated_at = datetime.utcnow()
                
                saved_playlists.append(existing_playlist)
            else:
                # Create new record
                new_playlist = UserPlaylist(
                    user_id=user_id,
                    playlist_id=playlist_data['playlist_id'],
                    playlist_name=playlist_data['playlist_name']
                )
                
                db.add(new_playlist)
                saved_playlists.append(new_playlist)
        
        db.commit()
        logger.info(f"Successfully saved/updated {len(saved_playlists)} playlists to database")
        return saved_playlists
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving playlists to database: {str(e)}")
        raise Exception(f"Error saving playlists to database: {str(e)}")


def _get_playlists_from_database(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
    """Get playlists from database"""
    try:
        playlists = db.exec(
            select(UserPlaylist).where(UserPlaylist.user_id == user_id)
        ).all()
        
        playlists_data = []
        for playlist in playlists:
            playlist_data = {
                'playlist_id': playlist.playlist_id,
                'playlist_name': playlist.playlist_name
            }
            playlists_data.append(playlist_data)
        
        logger.info(f"Retrieved {len(playlists_data)} playlists from database")
        return playlists_data
        
    except Exception as e:
        logger.error(f"Error retrieving playlists from database: {str(e)}")
        return []


def _get_cached_playlist_details_from_database(user_id: UUID, playlist_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get cached playlist details from database
    
    Args:
        user_id: UUID of the user
        playlist_id: YouTube playlist ID
        db: Database session
        
    Returns:
        Cached playlist details or None if not found
    """
    try:
        # Get playlist from user_playlist table
        playlist = db.exec(
            select(UserPlaylist).where(
                UserPlaylist.user_id == user_id,
                UserPlaylist.playlist_id == playlist_id
            )
        ).first()
        
        if not playlist:
            return None
        
        # Get top 2 videos from single_video_details table
        top_videos = []
        
        # Get top video by views
        if playlist.top_video_by_views_id:
            top_video_by_views = db.exec(
                select(SingleVideoDetails).where(
                    SingleVideoDetails.video_id == playlist.top_video_by_views_id,
                    SingleVideoDetails.user_id == user_id
                )
            ).first()
            
            if top_video_by_views:
                top_videos.append({
                    "video_id": top_video_by_views.video_id,
                    "title": top_video_by_views.title,
                    "description": top_video_by_views.description,
                    "thumbnail_url": top_video_by_views.thumbnail_link,
                    "duration": None,  # Not stored in single_video_details
                    "published_at": top_video_by_views.published_at.isoformat() if top_video_by_views.published_at else None,
                    "view_count": top_video_by_views.view_count,
                    "like_count": top_video_by_views.like_count,
                    "comment_count": top_video_by_views.comment_count,
                    "privacy_status": top_video_by_views.privacy_status,
                    "watch_time_minutes": top_video_by_views.watch_time_minutes,
                    "youtube_video_url": top_video_by_views.youtube_video_url,
                    "performance_type": "top_by_views"
                })
        
        # Get top video by likes (if different from top by views)
        if playlist.top_video_by_likes_id and playlist.top_video_by_likes_id != playlist.top_video_by_views_id:
            top_video_by_likes = db.exec(
                select(SingleVideoDetails).where(
                    SingleVideoDetails.video_id == playlist.top_video_by_likes_id,
                    SingleVideoDetails.user_id == user_id
                )
            ).first()
            
            if top_video_by_likes:
                top_videos.append({
                    "video_id": top_video_by_likes.video_id,
                    "title": top_video_by_likes.title,
                    "description": top_video_by_likes.description,
                    "thumbnail_url": top_video_by_likes.thumbnail_link,
                    "duration": None,  # Not stored in single_video_details
                    "published_at": top_video_by_likes.published_at.isoformat() if top_video_by_likes.published_at else None,
                    "view_count": top_video_by_likes.view_count,
                    "like_count": top_video_by_likes.like_count,
                    "comment_count": top_video_by_likes.comment_count,
                    "privacy_status": top_video_by_likes.privacy_status,
                    "watch_time_minutes": top_video_by_likes.watch_time_minutes,
                    "youtube_video_url": top_video_by_likes.youtube_video_url,
                    "performance_type": "top_by_likes"
                })
        
        # Create analytics data
        analytics = {
            "total_views": playlist.total_views,
            "total_likes": playlist.total_likes,
            "total_comments": playlist.total_comments,
            "average_engagement_rate": playlist.average_engagement_rate,
            "top_video_by_views": {
                "video_id": playlist.top_video_by_views_id,
                "title": playlist.top_video_by_views_title,
                "count": playlist.top_video_by_views_count
            },
            "top_video_by_likes": {
                "video_id": playlist.top_video_by_likes_id,
                "title": playlist.top_video_by_likes_title,
                "count": playlist.top_video_by_likes_count
            },
            "last_analytics_update": playlist.last_analytics_update.isoformat() if playlist.last_analytics_update else None
        }
        
        return {
            "playlist_id": playlist.playlist_id,
            "playlist_name": playlist.playlist_name,
            "description": None,  # Not stored in user_playlist table
            "thumbnail_url": None,  # Not stored in user_playlist table
            "video_count": 0,  # Not stored in user_playlist table
            "published_at": None,  # Not stored in user_playlist table
            "channel_title": None,  # Not stored in user_playlist table
            "privacy_status": None,  # Not stored in user_playlist table
            "top_videos": top_videos,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error retrieving cached playlist details from database: {str(e)}")
        return None


def get_playlist_details_service(user_id: UUID, playlist_id: str, db: Session, refresh: bool = False) -> Dict[str, Any]:
    """
    Get detailed information about a specific playlist.
    
    Args:
        user_id: UUID of the user
        playlist_id: YouTube playlist ID
        db: Database session
        refresh: If True, fetch fresh data from YouTube API and update database.
                If False, return cached data from database if exists, otherwise fetch from YouTube API and save to database.
    
    Returns:
        Dict containing success status, message, and playlist details
    """
    try:
        logger.info(f"Fetching playlist details for user_id: {user_id}, playlist_id: {playlist_id}, refresh: {refresh}")
        
        if not refresh:
            # Try to get cached data from database first
            cached_playlist = _get_cached_playlist_details_from_database(user_id, playlist_id, db)
            if cached_playlist:
                logger.info(f"Returning cached playlist details for playlist {playlist_id}")
                return {
                    "success": True,
                    "message": f"Playlist details retrieved from cache successfully",
                    "data": cached_playlist
                }
        
        # Get YouTube Data API client
        youtube_client = get_youtube_client(user_id, db)
        if not youtube_client:
            return {
                "success": False,
                "message": "Failed to authenticate with YouTube API",
                "data": None
            }
        
        # Fetch playlist details from YouTube API
        playlist_details = _fetch_playlist_details_from_youtube(youtube_client, playlist_id)
        
        if "error" in playlist_details:
            return {
                "success": False,
                "message": playlist_details["error"],
                "data": None
            }
        
        # Fetch top performing videos from playlist
        top_videos = _fetch_top_playlist_videos_from_youtube(youtube_client, playlist_id)
        
        if "error" in top_videos:
            logger.warning(f"Could not fetch top videos for playlist {playlist_id}: {top_videos['error']}")
            playlist_details["top_videos"] = []
            playlist_details["analytics"] = None
        else:
            playlist_details["top_videos"] = top_videos.get("videos", [])
            
            # Store all videos in SingleVideoDetails table
            _store_playlist_videos_in_database(
                user_id, playlist_id, playlist_details.get('playlist_name', ''), 
                top_videos.get("all_videos", []), db
            )
            
            # Calculate and store analytics
            analytics_data = _calculate_and_store_playlist_analytics(
                user_id, playlist_id, playlist_details, top_videos.get("all_videos", []), db
            )
            playlist_details["analytics"] = analytics_data
        
        return {
            "success": True,
            "message": f"Playlist details retrieved successfully",
            "data": playlist_details
        }
        
    except Exception as e:
        logger.error(f"Error retrieving playlist details for user_id {user_id}, playlist_id {playlist_id}: {str(e)}")
        return {
            "success": False,
            "message": f"Error retrieving playlist details: {str(e)}",
            "data": None
        }


def _fetch_playlist_details_from_youtube(youtube_client, playlist_id: str) -> Dict[str, Any]:
    """Fetch detailed playlist information from YouTube Data API"""
    try:
        # Get playlist details
        playlist_response = youtube_client.playlists().list(
            part='snippet,contentDetails,status',
            id=playlist_id
        ).execute()
        
        if not playlist_response.get('items'):
            return {"error": f"Playlist with ID {playlist_id} not found"}
        
        playlist = playlist_response['items'][0]
        snippet = playlist.get('snippet', {})
        content_details = playlist.get('contentDetails', {})
        status = playlist.get('status', {})
        
        # Extract thumbnail URL
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = None
        if thumbnails:
            # Try to get the highest quality thumbnail available
            for quality in ['maxres', 'high', 'medium', 'default']:
                if quality in thumbnails:
                    thumbnail_url = thumbnails[quality]['url']
                    break
        
        playlist_details = {
            'playlist_id': playlist_id,
            'playlist_name': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'thumbnail_url': thumbnail_url,
            'video_count': content_details.get('itemCount', 0),
            'published_at': snippet.get('publishedAt', ''),
            'channel_title': snippet.get('channelTitle', ''),
            'privacy_status': status.get('privacyStatus', '')
        }
        
        return playlist_details
        
    except Exception as e:
        logger.error(f"Error fetching playlist details from YouTube: {str(e)}")
        return {"error": f"Error fetching playlist details from YouTube: {str(e)}"}


def _fetch_top_playlist_videos_from_youtube(youtube_client, playlist_id: str) -> Dict[str, Any]:
    """Fetch top 2 videos from a playlist: one with highest likes and one with highest views"""
    try:
        all_videos = []
        next_page_token = None
        
        # Fetch all videos first to get complete statistics
        while True:
            # Get playlist items
            playlist_items_response = youtube_client.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
            # Extract video IDs
            video_ids = []
            for item in playlist_items_response.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
            
            if video_ids:
                # Get video details with all necessary parts
                videos_response = youtube_client.videos().list(
                    part='snippet,statistics,contentDetails,status',
                    id=','.join(video_ids)
                ).execute()
                
                for video in videos_response.get('items', []):
                    snippet = video.get('snippet', {})
                    statistics = video.get('statistics', {})
                    content_details = video.get('contentDetails', {})
                    status = video.get('status', {})
                    
                    # Extract video thumbnail
                    thumbnails = snippet.get('thumbnails', {})
                    video_thumbnail = None
                    if thumbnails:
                        for quality in ['maxres', 'high', 'medium', 'default']:
                            if quality in thumbnails:
                                video_thumbnail = thumbnails[quality]['url']
                                break
                    
                    # Get performance metrics
                    view_count = int(statistics.get('viewCount', 0))
                    like_count = int(statistics.get('likeCount', 0))
                    comment_count = int(statistics.get('commentCount', 0))
                    
                    # Get additional metrics
                    duration = content_details.get('duration', '')
                    privacy_status = status.get('privacyStatus', 'public')
                    
                    # Calculate watch time (if available in statistics)
                    watch_time_minutes = None
                    if 'averageViewDuration' in statistics:
                        # Convert ISO 8601 duration to minutes
                        avg_duration = statistics.get('averageViewDuration', '')
                        if avg_duration:
                            try:
                                # Parse PT1M30S format to minutes
                                import re
                                match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', avg_duration)
                                if match:
                                    hours = int(match.group(1) or 0)
                                    minutes = int(match.group(2) or 0)
                                    seconds = int(match.group(3) or 0)
                                    watch_time_minutes = hours * 60 + minutes + seconds / 60
                            except Exception as e:
                                logger.warning(f"Error parsing watch time for video {video['id']}: {str(e)}")
                    
                    video_data = {
                        'video_id': video['id'],
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'thumbnail_url': video_thumbnail,
                        'published_at': snippet.get('publishedAt', ''),
                        'duration': duration,
                        'view_count': view_count,
                        'like_count': like_count,
                        'comment_count': comment_count,
                        'privacy_status': privacy_status,
                        'watch_time_minutes': watch_time_minutes
                    }
                    
                    all_videos.append(video_data)
            
            next_page_token = playlist_items_response.get('nextPageToken')
            if not next_page_token:
                break
        
        if not all_videos:
            return {"videos": []}
        
        # Find top video by views
        top_by_views = max(all_videos, key=lambda x: x['view_count'])
        
        # Find top video by likes
        top_by_likes = max(all_videos, key=lambda x: x['like_count'])
        
        # Prepare result with exactly 2 videos
        result_videos = []
        
        # Add top by views
        top_by_views['performance_type'] = 'top_by_views'
        result_videos.append(top_by_views)
        
        # Add top by likes (only if it's different from top by views)
        if top_by_likes['video_id'] != top_by_views['video_id']:
            top_by_likes['performance_type'] = 'top_by_likes'
            result_videos.append(top_by_likes)
        else:
            # If same video is top in both, find second best by likes
            videos_sorted_by_likes = sorted(all_videos, key=lambda x: x['like_count'], reverse=True)
            if len(videos_sorted_by_likes) > 1:
                second_best_by_likes = videos_sorted_by_likes[1]
                second_best_by_likes['performance_type'] = 'top_by_likes'
                result_videos.append(second_best_by_likes)
        
        logger.info(f"Retrieved {len(all_videos)} total videos, returning top 2: {len(result_videos)} videos")
        logger.info(f"Top by views: {top_by_views['title']} ({top_by_views['view_count']:,} views)")
        if len(result_videos) > 1:
            logger.info(f"Top by likes: {result_videos[1]['title']} ({result_videos[1]['like_count']:,} likes)")
        
        return {
            "videos": result_videos,
            "all_videos": all_videos  # Include all videos for analytics calculation
        }
        
    except Exception as e:
        logger.error(f"Error fetching top playlist videos from YouTube: {str(e)}")
        return {"error": f"Error fetching top playlist videos from YouTube: {str(e)}"}


def _calculate_and_store_playlist_analytics(
    user_id: UUID, 
    playlist_id: str, 
    playlist_details: Dict[str, Any], 
    all_videos: List[Dict[str, Any]], 
    db: Session
) -> Dict[str, Any]:
    """Calculate and store playlist analytics in the database"""
    try:
        if not all_videos:
            logger.warning(f"No videos found for analytics calculation for playlist {playlist_id}")
            return None
        
        # Calculate analytics
        total_views = sum(video.get('view_count', 0) for video in all_videos)
        total_likes = sum(video.get('like_count', 0) for video in all_videos)
        total_comments = sum(video.get('comment_count', 0) for video in all_videos)
        
        # Calculate average engagement rate
        total_engagement = 0
        videos_with_views = 0
        for video in all_videos:
            view_count = video.get('view_count', 0)
            if view_count > 0:
                like_count = video.get('like_count', 0)
                comment_count = video.get('comment_count', 0)
                engagement_rate = (like_count + comment_count) / view_count
                total_engagement += engagement_rate
                videos_with_views += 1
        
        average_engagement_rate = total_engagement / videos_with_views if videos_with_views > 0 else 0
        
        # Find top videos
        top_by_views = max(all_videos, key=lambda x: x.get('view_count', 0))
        top_by_likes = max(all_videos, key=lambda x: x.get('like_count', 0))
        
        # Prepare analytics data
        analytics_data = {
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'average_engagement_rate': round(average_engagement_rate, 4),
            'top_video_by_views_id': top_by_views.get('video_id'),
            'top_video_by_likes_id': top_by_likes.get('video_id'),
            'top_video_by_views_title': top_by_views.get('title'),
            'top_video_by_likes_title': top_by_likes.get('title'),
            'top_video_by_views_count': top_by_views.get('view_count', 0),
            'top_video_by_likes_count': top_by_likes.get('like_count', 0),
            'last_analytics_update': datetime.utcnow().isoformat()
        }
        
        # Store analytics in database
        _update_playlist_analytics_in_database(user_id, playlist_id, analytics_data, db)
        
        logger.info(f"Calculated analytics for playlist {playlist_id}: {total_views:,} total views, {total_likes:,} total likes")
        
        return analytics_data
        
    except Exception as e:
        logger.error(f"Error calculating playlist analytics for playlist {playlist_id}: {str(e)}")
        return None


def _update_playlist_analytics_in_database(
    user_id: UUID, 
    playlist_id: str, 
    analytics_data: Dict[str, Any], 
    db: Session
) -> None:
    """Update playlist analytics in the database"""
    try:
        # Find existing playlist record
        existing_playlist = db.exec(
            select(UserPlaylist).where(
                UserPlaylist.user_id == user_id,
                UserPlaylist.playlist_id == playlist_id
            )
        ).first()
        
        if existing_playlist:
            # Update existing record with analytics
            existing_playlist.total_views = analytics_data['total_views']
            existing_playlist.total_likes = analytics_data['total_likes']
            existing_playlist.total_comments = analytics_data['total_comments']
            existing_playlist.average_engagement_rate = analytics_data['average_engagement_rate']
            existing_playlist.top_video_by_views_id = analytics_data['top_video_by_views_id']
            existing_playlist.top_video_by_likes_id = analytics_data['top_video_by_likes_id']
            existing_playlist.top_video_by_views_title = analytics_data['top_video_by_views_title']
            existing_playlist.top_video_by_likes_title = analytics_data['top_video_by_likes_title']
            existing_playlist.top_video_by_views_count = analytics_data['top_video_by_views_count']
            existing_playlist.top_video_by_likes_count = analytics_data['top_video_by_likes_count']
            existing_playlist.last_analytics_update = datetime.utcnow()
            existing_playlist.updated_at = datetime.utcnow()
        else:
            # Create new record with analytics
            new_playlist = UserPlaylist(
                user_id=user_id,
                playlist_id=playlist_id,
                playlist_name=analytics_data.get('playlist_name', ''),
                total_views=analytics_data['total_views'],
                total_likes=analytics_data['total_likes'],
                total_comments=analytics_data['total_comments'],
                average_engagement_rate=analytics_data['average_engagement_rate'],
                top_video_by_views_id=analytics_data['top_video_by_views_id'],
                top_video_by_likes_id=analytics_data['top_video_by_likes_id'],
                top_video_by_views_title=analytics_data['top_video_by_views_title'],
                top_video_by_likes_title=analytics_data['top_video_by_likes_title'],
                top_video_by_views_count=analytics_data['top_video_by_views_count'],
                top_video_by_likes_count=analytics_data['top_video_by_likes_count'],
                last_analytics_update=datetime.utcnow()
            )
            db.add(new_playlist)
        
        db.commit()
        logger.info(f"Successfully updated analytics for playlist {playlist_id} in database")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating playlist analytics in database: {str(e)}")
        raise Exception(f"Error updating playlist analytics in database: {str(e)}")


def _store_playlist_videos_in_database(
    user_id: UUID,
    playlist_id: str,
    playlist_name: str,
    all_videos: List[Dict[str, Any]],
    db: Session
) -> None:
    """Store all playlist videos in the SingleVideoDetails table"""
    try:
        stored_count = 0
        updated_count = 0
        
        for video_data in all_videos:
            video_id = video_data.get('video_id')
            if not video_id:
                continue
            
            # Check if video already exists
            existing_video = db.exec(
                select(SingleVideoDetails).where(
                    SingleVideoDetails.user_id == user_id,
                    SingleVideoDetails.video_id == video_id
                )
            ).first()
            
            # Calculate additional analytics
            published_at_str = video_data.get('published_at', '')
            published_at = None
            days_since_published = None
            views_per_day = None
            
            if published_at_str:
                try:
                    published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                    days_since_published = (datetime.utcnow() - published_at.replace(tzinfo=None)).days
                    view_count = video_data.get('view_count', 0)
                    views_per_day = view_count / max(days_since_published, 1) if days_since_published > 0 else 0
                except Exception as e:
                    logger.warning(f"Error parsing published date for video {video_id}: {str(e)}")
            
            # Prepare video data for storage
            video_record_data = {
                'video_id': video_id,
                'user_id': user_id,
                'title': video_data.get('title', ''),
                'description': video_data.get('description', ''),
                'thumbnail_link': video_data.get('thumbnail_url', ''),
                'playlist': playlist_name,
                'privacy_status': video_data.get('privacy_status', 'public'),
                'view_count': video_data.get('view_count', 0),
                'like_count': video_data.get('like_count', 0),
                'comment_count': video_data.get('comment_count', 0),
                'watch_time_minutes': video_data.get('watch_time_minutes'),
                'published_at': published_at,
                'youtube_video_url': f"https://www.youtube.com/watch?v={video_id}",
                'days_since_published': days_since_published,
                'views_per_day': round(views_per_day, 2) if views_per_day else None,
                'updated_at': datetime.utcnow()
            }
            
            if existing_video:
                # Update existing record
                for key, value in video_record_data.items():
                    if key != 'video_id' and key != 'user_id':  # Don't update primary keys
                        setattr(existing_video, key, value)
                updated_count += 1
            else:
                # Create new record
                new_video = SingleVideoDetails(**video_record_data)
                db.add(new_video)
                stored_count += 1
        
        db.commit()
        logger.info(f"Successfully stored {stored_count} new videos and updated {updated_count} existing videos for playlist {playlist_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing playlist videos in database: {str(e)}")
        raise Exception(f"Error storing playlist videos in database: {str(e)}")


def get_playlist_all_videos_service(user_id: UUID, playlist_id: str, db: Session, refresh: bool = False) -> Dict[str, Any]:
    """
    Get all videos from a specific playlist.
    
    Args:
        user_id: UUID of the user
        playlist_id: YouTube playlist ID
        db: Database session
        refresh: If True, always fetch fresh data from YouTube API.
                If False, return cached data from database if available.
    
    Returns:
        Dict containing success status, message, and all videos data
    """
    try:
        logger.info(f"Fetching all videos for playlist: {playlist_id}, user_id: {user_id}, refresh: {refresh}")
        
        if not refresh:
            # Try to get cached data from database first
            cached_videos = _get_cached_playlist_videos_from_database(user_id, playlist_id, db)
            if cached_videos:
                logger.info(f"Returning cached videos for playlist {playlist_id}: {len(cached_videos)} videos")
                return {
                    "success": True,
                    "message": f"Retrieved {len(cached_videos)} cached videos from database",
                    "data": {
                        "playlist_id": playlist_id,
                        "playlist_name": cached_videos[0].get('playlist_name', '') if cached_videos else '',
                        "total_videos": len(cached_videos),
                        "videos": cached_videos
                    }
                }
        
        # Get YouTube Data API client
        youtube_client = get_youtube_client(user_id, db)
        if not youtube_client:
            return {
                "success": False,
                "message": "Failed to authenticate with YouTube API",
                "data": None
            }
        
        # Fetch playlist basic info
        playlist_info = _fetch_playlist_basic_info(youtube_client, playlist_id)
        if "error" in playlist_info:
            return {
                "success": False,
                "message": playlist_info["error"],
                "data": None
            }
        
        # Fetch all videos from playlist
        all_videos_result = _fetch_all_playlist_videos_from_youtube(youtube_client, playlist_id)
        
        if "error" in all_videos_result:
            return {
                "success": False,
                "message": all_videos_result["error"],
                "data": None
            }
        
        all_videos = all_videos_result.get("videos", [])
        
        # Store all videos in database
        _store_playlist_videos_in_database(
            user_id, playlist_id, playlist_info.get('playlist_name', ''), 
            all_videos, db
        )
        
        message = f"Retrieved {len(all_videos)} videos from playlist successfully"
        if refresh:
            message += " (refreshed from YouTube API)"
        else:
            message += " (fetched from YouTube API and cached)"
        
        return {
            "success": True,
            "message": message,
            "data": {
                "playlist_id": playlist_id,
                "playlist_name": playlist_info.get('playlist_name', ''),
                "total_videos": len(all_videos),
                "videos": all_videos
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving all videos for playlist {playlist_id}: {str(e)}")
        return {
            "success": False,
            "message": f"Error retrieving playlist videos: {str(e)}",
            "data": None
        }


def _fetch_playlist_basic_info(youtube_client, playlist_id: str) -> Dict[str, Any]:
    """Fetch basic playlist information"""
    try:
        playlist_response = youtube_client.playlists().list(
            part='snippet',
            id=playlist_id
        ).execute()
        
        if not playlist_response.get('items'):
            return {"error": f"Playlist with ID {playlist_id} not found"}
        
        playlist = playlist_response['items'][0]
        snippet = playlist.get('snippet', {})
        
        return {
            "playlist_name": snippet.get('title', ''),
            "description": snippet.get('description', '')
        }
        
    except Exception as e:
        logger.error(f"Error fetching playlist basic info: {str(e)}")
        return {"error": f"Error fetching playlist info: {str(e)}"}


def _fetch_all_playlist_videos_from_youtube(youtube_client, playlist_id: str) -> Dict[str, Any]:
    """Fetch all videos from a playlist with complete details"""
    try:
        all_videos = []
        next_page_token = None
        
        # Fetch all videos with pagination
        while True:
            # Get playlist items
            playlist_items_response = youtube_client.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
            # Extract video IDs
            video_ids = []
            for item in playlist_items_response.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
            
            if video_ids:
                # Get video details with all necessary parts
                videos_response = youtube_client.videos().list(
                    part='snippet,statistics,contentDetails,status',
                    id=','.join(video_ids)
                ).execute()
                
                for video in videos_response.get('items', []):
                    snippet = video.get('snippet', {})
                    statistics = video.get('statistics', {})
                    content_details = video.get('contentDetails', {})
                    status = video.get('status', {})
                    
                    # Extract video thumbnail
                    thumbnails = snippet.get('thumbnails', {})
                    video_thumbnail = None
                    if thumbnails:
                        for quality in ['maxres', 'high', 'medium', 'default']:
                            if quality in thumbnails:
                                video_thumbnail = thumbnails[quality]['url']
                                break
                    
                    # Get performance metrics
                    view_count = int(statistics.get('viewCount', 0))
                    like_count = int(statistics.get('likeCount', 0))
                    comment_count = int(statistics.get('commentCount', 0))
                    
                    # Get additional metrics
                    duration = content_details.get('duration', '')
                    privacy_status = status.get('privacyStatus', 'public')
                    
                    # Calculate watch time (if available in statistics)
                    watch_time_minutes = None
                    if 'averageViewDuration' in statistics:
                        # Convert ISO 8601 duration to minutes
                        avg_duration = statistics.get('averageViewDuration', '')
                        if avg_duration:
                            try:
                                # Parse PT1M30S format to minutes
                                import re
                                match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', avg_duration)
                                if match:
                                    hours = int(match.group(1) or 0)
                                    minutes = int(match.group(2) or 0)
                                    seconds = int(match.group(3) or 0)
                                    watch_time_minutes = hours * 60 + minutes + seconds / 60
                            except Exception as e:
                                logger.warning(f"Error parsing watch time for video {video['id']}: {str(e)}")
                    
                    video_data = {
                        'video_id': video['id'],
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'thumbnail_url': video_thumbnail,
                        'published_at': snippet.get('publishedAt', ''),
                        'duration': duration,
                        'view_count': view_count,
                        'like_count': like_count,
                        'comment_count': comment_count,
                        'privacy_status': privacy_status,
                        'watch_time_minutes': watch_time_minutes,
                        'youtube_video_url': f"https://www.youtube.com/watch?v={video['id']}"
                    }
                    
                    all_videos.append(video_data)
            
            next_page_token = playlist_items_response.get('nextPageToken')
            if not next_page_token:
                break
        
        logger.info(f"Retrieved {len(all_videos)} total videos from playlist")
        return {"videos": all_videos}
        
    except Exception as e:
        logger.error(f"Error fetching all playlist videos from YouTube: {str(e)}")
        return {"error": f"Error fetching playlist videos from YouTube: {str(e)}"}


def _get_cached_playlist_videos_from_database(user_id: UUID, playlist_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get cached playlist videos from the database"""
    try:
        # Get videos from SingleVideoDetails table for this playlist
        videos = db.exec(
            select(SingleVideoDetails).where(
                SingleVideoDetails.user_id == user_id,
                SingleVideoDetails.playlist == playlist_id
            )
        ).all()
        
        if not videos:
            logger.info(f"No cached videos found for playlist {playlist_id}")
            return []
        
        # Convert to the expected format
        cached_videos = []
        for video in videos:
            video_data = {
                'video_id': video.video_id,
                'title': video.title or '',
                'description': video.description or '',
                'thumbnail_url': video.thumbnail_link or '',
                'published_at': video.published_at.isoformat() if video.published_at else '',
                'duration': '',  # Not stored in SingleVideoDetails
                'view_count': video.view_count or 0,
                'like_count': video.like_count or 0,
                'comment_count': video.comment_count or 0,
                'privacy_status': video.privacy_status or 'public',
                'watch_time_minutes': video.watch_time_minutes,
                'youtube_video_url': video.youtube_video_url or f"https://www.youtube.com/watch?v={video.video_id}",
                'playlist_name': video.playlist or ''
            }
            cached_videos.append(video_data)
        
        logger.info(f"Retrieved {len(cached_videos)} cached videos from database for playlist {playlist_id}")
        return cached_videos
        
    except Exception as e:
        logger.error(f"Error retrieving cached videos from database: {str(e)}")
        return []
