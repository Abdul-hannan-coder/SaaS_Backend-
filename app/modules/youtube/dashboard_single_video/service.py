"""
Service layer for single video details
"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import Session, select
from uuid import UUID

from .model import SingleVideoDetails, SingleVideoDetailsResponse, SingleVideoResponse, UpdateVideoRequest, UpdateVideoResponse, DeleteVideoResponse
from ..helpers.youtube_client import get_youtube_client
from ..helpers.transcript_dependency import _fetch_transcript_from_youtube
from ....utils.my_logger import get_logger
import json
from fastapi import UploadFile, File
from ..helpers.image_upload import upload_custom_thumbnail
from ..thumbnail_generator.error_models import ValidationError, DatabaseError
from ..helpers.download_image_from_url import download_image_from_url
logger = get_logger("SINGLE_VIDEO_SERVICE")


def _fetch_transcript_only(video_id: str, user_id: UUID, db: Session) -> Optional[str]:
    """
    Fetch only transcript for a video without fetching all video data
    
    Args:
        video_id: YouTube video ID
        user_id: User ID
        db: Database session
        
    Returns:
        Transcript data as JSON string or None if not available
    """
    try:
        # Get YouTube client for captions API
        youtube_client = get_youtube_client(user_id, db)
        if not youtube_client:
            logger.error(f"Failed to get YouTube client for transcript fetch for video_id {video_id}")
            return None
        
        # Try third-party transcript API first
        try:
            logger.info(f"Attempting to fetch transcript for video {video_id} using third-party API")
            transcript_result = _fetch_transcript_from_youtube(video_id)
            if transcript_result:
                transcript_data = json.dumps(transcript_result, ensure_ascii=False)
                logger.info(f"Successfully fetched transcript for video {video_id} using third-party API")
                return transcript_data
            else:
                logger.warning(f"No transcript available for video {video_id} using third-party API")
                raise Exception("Third-party API returned None")
        except Exception as e:
            logger.warning(f"Third-party transcript API failed for video {video_id}: {e}")
            
            # Fallback to official YouTube Captions API
            try:
                logger.info(f"Attempting to fetch captions for video {video_id} using official YouTube API")
                transcript_result = _fetch_captions_from_youtube_api(youtube_client, video_id)
                if transcript_result:
                    transcript_data = json.dumps(transcript_result, ensure_ascii=False)
                    logger.info(f"Successfully fetched captions for video {video_id} using official YouTube API")
                    return transcript_data
                else:
                    logger.warning(f"No captions available for video {video_id} using official YouTube API")
                    return None
            except Exception as e2:
                logger.warning(f"Official YouTube Captions API also failed for video {video_id}: {e2}")
                return None
                
    except Exception as e:
        logger.error(f"Error fetching transcript for video {video_id}: {e}")
        return None


def _fetch_captions_from_youtube_api(youtube_client, video_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch captions from YouTube using official Captions API
    
    Args:
        youtube_client: Authenticated YouTube API client
        video_id: YouTube video ID
        
    Returns:
        Caption data or None if not available
    """
    try:
        # List available captions for the video
        captions_response = youtube_client.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()
        
        if not captions_response.get('items'):
            logger.info(f"No captions available for video {video_id}")
            return None
        
        # Find the best caption track (prefer English, then any available)
        caption_track = None
        for item in captions_response['items']:
            snippet = item.get('snippet', {})
            language = snippet.get('language', '')
            
            # Prefer English captions
            if language == 'en':
                caption_track = item
                break
            # Fallback to any available caption
            elif not caption_track:
                caption_track = item
        
        if not caption_track:
            logger.info(f"No suitable caption track found for video {video_id}")
            return None
        
        caption_id = caption_track['id']
        language = caption_track['snippet']['language']
        
        # Download the caption content
        caption_content = youtube_client.captions().download(
            id=caption_id,
            tfmt='srt'  # SRT format
        ).execute()
        
        # Parse SRT content (basic parsing)
        if caption_content:
            # Convert SRT to our format
            transcript_segments = []
            lines = caption_content.decode('utf-8').split('\n')
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.isdigit():  # Sequence number
                    i += 1
                    if i < len(lines):
                        time_line = lines[i].strip()
                        i += 1
                        if i < len(lines):
                            text_line = lines[i].strip()
                            if text_line:
                                # Parse time (00:00:00,000 --> 00:00:03,000)
                                if ' --> ' in time_line:
                                    start_time, end_time = time_line.split(' --> ')
                                    transcript_segments.append({
                                        'text': text_line,
                                        'start': start_time,
                                        'duration': end_time
                                    })
                i += 1
            
            return {
                'segments': transcript_segments,
                'source': 'youtube_captions_api',
                'language': language,
                'fetched_at': datetime.utcnow().isoformat()
            }
        
        return None
        
    except Exception as e:
        logger.warning(f"Error fetching captions from YouTube API for video {video_id}: {e}")
        return None


def get_single_video_details_service(video_id: str, user_id: UUID, db: Session, refresh: bool = False) -> Dict[str, Any]:
    """Get video details by video ID for a specific user"""
    try:
        # Check if video details exist in database for this user
        statement = select(SingleVideoDetails).where(
            SingleVideoDetails.video_id == video_id,
            SingleVideoDetails.user_id == user_id
        )
        video_details = db.exec(statement).first()
        
        # Determine if we need to fetch from YouTube
        should_fetch_from_youtube = refresh or not video_details
        
        # Check if we need to fetch transcript specifically (even if refresh=False)
        needs_transcript_fetch = False
        if video_details and not video_details.transcript:
            needs_transcript_fetch = True
            logger.info(f"Video exists in database but transcript is missing for video_id {video_id}")
        
        if should_fetch_from_youtube:
            # Fetch from YouTube API
            youtube_data = _fetch_from_youtube_api(video_id, user_id, db)
            
            if "error" in youtube_data:
                return {
                    "success": False,
                    "message": youtube_data["error"],
                    "video_details": None,
                    "refreshed": refresh
                }
            
            # Save to database
            video_details = _save_to_database(video_id, youtube_data, user_id, db)
            message = "Video details refreshed from YouTube successfully" if refresh else "Video details fetched from YouTube and saved to database"
            logger.info(f"Successfully {'refreshed' if refresh else 'fetched'} video details for video_id {video_id}")
            
        elif needs_transcript_fetch:
            # Video exists but transcript is missing - fetch only transcript
            logger.info(f"Fetching missing transcript for video_id {video_id}")
            transcript_data = _fetch_transcript_only(video_id, user_id, db)
            
            if transcript_data:
                # Update only the transcript field in database
                video_details.transcript = transcript_data
                db.add(video_details)
                db.commit()
                db.refresh(video_details)
                logger.info(f"Successfully fetched and saved transcript for video_id {video_id}")
                message = "Video details retrieved from database, transcript fetched and updated"
            else:
                logger.warning(f"Failed to fetch transcript for video_id {video_id}")
                message = "Video details retrieved from database, transcript not available"
        else:
            message = "Video details retrieved from database successfully"
            logger.info(f"Successfully retrieved video details from database for video_id {video_id}")
        
        # Create response
        response_details = SingleVideoDetailsResponse(
            video_id=video_id,
            title=video_details.title,
            description=video_details.description,
            thumbnail_link=video_details.thumbnail_link,
            playlist=video_details.playlist,
            playlist_name=video_details.playlist_name,
            privacy_status=video_details.privacy_status,
            transcript=video_details.transcript,
            custom_thumbnail_path=video_details.custom_thumbnail_path,
            
            # Analytics fields
            view_count=video_details.view_count,
            like_count=video_details.like_count,
            comment_count=video_details.comment_count,
            watch_time_minutes=video_details.watch_time_minutes,
            published_at=video_details.published_at,
            youtube_video_url=video_details.youtube_video_url,
            days_since_published=video_details.days_since_published,
            views_per_day=video_details.views_per_day,
            
            transcript_available=bool(video_details.transcript),
            transcript_source="database" if video_details.transcript else ("fetched" if needs_transcript_fetch else None)
        )
        
        return {
            "success": True,
            "message": message,
            "video_details": response_details.dict(),
            "refreshed": refresh
        }
        
    except Exception as e:
        logger.error(f"Error retrieving video details: {str(e)}")
        raise Exception(f"Error retrieving video details: {str(e)}")


def update_video_details_service(video_id: str, user_id: UUID, db: Session, update_data: UpdateVideoRequest) -> Dict[str, Any]:
    """Update video details on YouTube and in database"""
    try:
        # Get YouTube client
        youtube_client = get_youtube_client(user_id, db)
        if not youtube_client:
            return {
                "success": False,
                "message": "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens.",
                "updated_fields": [],
                "video_details": None
            }
        
        updated_fields = []
        
        # Update title and/or description
        if update_data.title is not None or update_data.description is not None:
            try:
                # First get current video details to preserve other fields
                current_video = youtube_client.videos().list(
                    part='snippet',
                    id=video_id
                ).execute()
                
                if not current_video.get('items'):
                    return {
                        "success": False,
                        "message": "Video not found on YouTube",
                        "updated_fields": [],
                        "video_details": None
                    }
                
                current_snippet = current_video['items'][0]['snippet']
                
                # Prepare update data
                update_snippet = {
                    'id': video_id,
                    'snippet': {
                        'title': update_data.title if update_data.title is not None else current_snippet['title'],
                        'description': update_data.description if update_data.description is not None else current_snippet['description'],
                        'categoryId': current_snippet.get('categoryId', '22')  # Required field
                    }
                }
                
                # Update on YouTube
                youtube_client.videos().update(
                    part='snippet',
                    body=update_snippet
                ).execute()
                
                if update_data.title is not None:
                    updated_fields.append('title')
                if update_data.description is not None:
                    updated_fields.append('description')
                    
                logger.info(f"Successfully updated title/description for video {video_id}")
                
            except Exception as e:
                logger.error(f"Error updating title/description: {str(e)}")
                return {
                    "success": False,
                    "message": f"Error updating title/description: {str(e)}",
                    "updated_fields": [],
                    "video_details": None
                }
        
        # Update privacy status
        if update_data.privacy_status is not None:
            try:
                youtube_client.videos().update(
                    part='status',
                    body={
                        'id': video_id,
                        'status': {
                            'privacyStatus': update_data.privacy_status
                        }
                    }
                ).execute()
                
                updated_fields.append('privacy_status')
                logger.info(f"Successfully updated privacy status for video {video_id}")
                
            except Exception as e:
                logger.error(f"Error updating privacy status: {str(e)}")
                return {
                    "success": False,
                    "message": f"Error updating privacy status: {str(e)}",
                    "updated_fields": updated_fields,
                    "video_details": None
                }
        
        # Handle playlist update
        if update_data.playlist_id is not None:
            if update_data.playlist_id.strip():  # Add to playlist if not empty
                try:
                    youtube_client.playlistItems().insert(
                        part='snippet',
                        body={
                            'snippet': {
                                'playlistId': update_data.playlist_id,
                                'resourceId': {
                                    'kind': 'youtube#video',
                                    'videoId': video_id
                                }
                            }
                        }
                    ).execute()
                    
                    updated_fields.append('playlist_added')
                    logger.info(f"Successfully added video {video_id} to playlist {update_data.playlist_id}")
                    
                except Exception as e:
                    logger.error(f"Error adding to playlist: {str(e)}")
                    return {
                        "success": False,
                        "message": f"Error adding to playlist: {str(e)}",
                        "updated_fields": updated_fields,
                        "video_details": None
                    }
            else:  # Remove from current playlist if empty string
                try:
                    # Get current video details to find current playlist
                    statement = select(SingleVideoDetails).where(
                        SingleVideoDetails.video_id == video_id,
                        SingleVideoDetails.user_id == user_id
                    )
                    current_video = db.exec(statement).first()
                    
                    if current_video and current_video.playlist:
                        # Find and remove from current playlist
                        playlist_items = youtube_client.playlistItems().list(
                            part='snippet',
                            playlistId=current_video.playlist,
                            videoId=video_id
                        ).execute()
                        
                        if playlist_items.get('items'):
                            playlist_item_id = playlist_items['items'][0]['id']
                            youtube_client.playlistItems().delete(
                                id=playlist_item_id
                            ).execute()
                            
                            updated_fields.append('playlist_removed')
                            logger.info(f"Successfully removed video {video_id} from playlist {current_video.playlist}")
                        else:
                            logger.warning(f"Video {video_id} not found in current playlist {current_video.playlist}")
                    else:
                        logger.info(f"Video {video_id} is not currently in any playlist")
                        
                except Exception as e:
                    logger.error(f"Error removing from playlist: {str(e)}")
                    return {
                        "success": False,
                        "message": f"Error removing from playlist: {str(e)}",
                        "updated_fields": updated_fields,
                        "video_details": None
                    }
        
        # If no fields were specified for update
        if not updated_fields:
            return {
                "success": False,
                "message": "No fields specified for update",
                "updated_fields": [],
                "video_details": None
            }
        
        # Update database with the changes we made
        try:
            # First try to fetch complete updated data from YouTube
            updated_video_data = _fetch_from_youtube_api(video_id, user_id, db)
            if "error" not in updated_video_data:
                # Save complete updated data to database
                _save_to_database(video_id, updated_video_data, user_id, db)
                logger.info(f"Successfully synced complete video data to database for video {video_id}")
            else:
                # If YouTube fetch fails, manually update the fields we changed
                logger.warning(f"Could not fetch complete updated data from YouTube: {updated_video_data['error']}")
                logger.info("Manually updating changed fields in database")
                
                # Get existing record
                statement = select(SingleVideoDetails).where(
                    SingleVideoDetails.video_id == video_id,
                    SingleVideoDetails.user_id == user_id
                )
                video_record = db.exec(statement).first()
                
                if video_record:
                    # Update only the fields we changed
                    if update_data.title is not None:
                        video_record.title = update_data.title
                    if update_data.description is not None:
                        video_record.description = update_data.description
                    if update_data.privacy_status is not None:
                        video_record.privacy_status = update_data.privacy_status
                    if update_data.playlist_id is not None:
                        if update_data.playlist_id.strip():
                            video_record.playlist = update_data.playlist_id
                        else:
                            video_record.playlist = None
                    
                    video_record.updated_at = datetime.utcnow()
                    db.add(video_record)
                    db.commit()
                    db.refresh(video_record)
                    logger.info(f"Successfully updated database manually for video {video_id}")
                else:
                    logger.error(f"Video record not found in database for video {video_id}")
                    
        except Exception as e:
            logger.error(f"Error updating database: {str(e)}")
            # Don't fail the entire operation if database update fails
            logger.warning("YouTube update succeeded but database sync failed")
        
        # Get final video details from database
        statement = select(SingleVideoDetails).where(
            SingleVideoDetails.video_id == video_id,
            SingleVideoDetails.user_id == user_id
        )
        video_details = db.exec(statement).first()
        
        response_details = None
        if video_details:
            response_details = SingleVideoDetailsResponse(
                video_id=video_details.video_id,
                title=video_details.title,
                description=video_details.description,
                thumbnail_link=video_details.thumbnail_link,
                playlist=video_details.playlist,
                privacy_status=video_details.privacy_status,
                custom_thumbnail_path=video_details.custom_thumbnail_path,
                
                # Analytics fields
                view_count=video_details.view_count,
                like_count=video_details.like_count,
                comment_count=video_details.comment_count,
                watch_time_minutes=video_details.watch_time_minutes,
                published_at=video_details.published_at,
                youtube_video_url=video_details.youtube_video_url,
                days_since_published=video_details.days_since_published,
                views_per_day=video_details.views_per_day
            )
        
        return {
            "success": True,
            "message": f"Successfully updated video fields: {', '.join(updated_fields)}",
            "updated_fields": updated_fields,
            "video_details": response_details.dict() if response_details else None
        }
        
    except Exception as e:
        logger.error(f"Error updating video details: {str(e)}")
        return {
            "success": False,
            "message": f"Error updating video details: {str(e)}",
            "updated_fields": [],
            "video_details": None
        }


def delete_video_service(video_id: str, user_id: UUID, db: Session) -> Dict[str, Any]:
    """Delete video from YouTube and remove from database"""
    try:
        # Get YouTube client
        youtube_client = get_youtube_client(user_id, db)
        if not youtube_client:
            return {
                "success": False,
                "message": "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens.",
                "deleted_video_id": None
            }
        
        # Check if video exists in our database (for user verification)
        statement = select(SingleVideoDetails).where(
            SingleVideoDetails.video_id == video_id,
            SingleVideoDetails.user_id == user_id
        )
        video_record = db.exec(statement).first()
        
        # Verify video exists on YouTube and user owns it
        try:
            # Check if video exists and user has access to it
            video_check = youtube_client.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not video_check.get('items'):
                return {
                    "success": False,
                    "message": "Video not found on YouTube or you don't have permission to delete it",
                    "deleted_video_id": None
                }
            
        except Exception as e:
            logger.error(f"Error checking video ownership: {str(e)}")
            return {
                "success": False,
                "message": f"Error verifying video ownership: {str(e)}",
                "deleted_video_id": None
            }
        
        # Delete video from YouTube
        try:
            youtube_client.videos().delete(id=video_id).execute()
            logger.info(f"Successfully deleted video {video_id} from YouTube")
            
        except Exception as e:
            logger.error(f"Error deleting video from YouTube: {str(e)}")
            return {
                "success": False,
                "message": f"Error deleting video from YouTube: {str(e)}",
                "deleted_video_id": None
            }
        
        # Remove video from our database if it exists
        if video_record:
            try:
                db.delete(video_record)
                db.commit()
                logger.info(f"Successfully removed video {video_id} from database")
                
            except Exception as e:
                logger.error(f"Error removing video from database: {str(e)}")
                # Don't fail the operation if database cleanup fails
                logger.warning("Video deleted from YouTube but database cleanup failed")
        
        return {
            "success": True,
            "message": "Video deleted successfully from YouTube and removed from database",
            "deleted_video_id": video_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        return {
            "success": False,
            "message": f"Error deleting video: {str(e)}",
            "deleted_video_id": None
        }




async def upload_custom_thumbnail_service(video_id: str, file: UploadFile , dir_path: str , user_id: UUID, db: Session) -> dict:
    """Upload custom thumbnail for a specific user"""
    result = await upload_custom_thumbnail(video_id, file, dir_path, db)
    # update the custom_thumbnail_path in the database  
    statement = select(SingleVideoDetails).where(
        SingleVideoDetails.video_id == video_id,
        SingleVideoDetails.user_id == user_id
    )
    video_details = db.exec(statement).first()
    
    if not video_details:
        raise ValidationError(
            "Video not found in database for the current user", 
            field="video_id", 
            value=video_id, 
            error_type="video_not_found"
        )
    
    video_details.custom_thumbnail_path = result["custom_thumbnail_path"]
    video_details.updated_at = datetime.utcnow()
    db.add(video_details)   
    db.commit()  # Add explicit commit
    return result



async def select_generated_thumbnail_service(video_id: str, url:str, user_id: UUID, db: Session, dir_path: str) -> dict:
    # download image from url 
    result = await download_image_from_url(url, dir_path, video_id)
    # update the custom_thumbnail_path in the database  
    statement = select(SingleVideoDetails).where(
        SingleVideoDetails.video_id == video_id,
        SingleVideoDetails.user_id == user_id
    )
    video_details = db.exec(statement).first()
    if not video_details:
        raise ValidationError(
            "Video not found in database for the current user", 
            field="video_id", 
            value=video_id, 
            error_type="video_not_found"
        )
    video_details.custom_thumbnail_path = result["custom_thumbnail_path"]
    video_details.updated_at = datetime.utcnow()
    db.add(video_details)
    db.commit()

    # and also create youtube client and upload to youtube 
    youtube_client = get_youtube_client(user_id, db)
    if not youtube_client:
        raise ValidationError(
            "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens.",
            field="user_id", 
            value=user_id, 
            error_type="youtube_client_not_found"
        )
    
    # Upload thumbnail to YouTube
    try:
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(result["custom_thumbnail_path"], mimetype='image/png')
        youtube_client.thumbnails().set(
            videoId=video_id,
            media_body=media
        ).execute()
        logger.info(f"Successfully uploaded thumbnail to YouTube for video {video_id}")
    except Exception as e:
        logger.warning(f"Failed to upload thumbnail to YouTube for video {video_id}: {e}")
        # Don't raise error here - the local save was successful
    
    video_details.updated_at = datetime.utcnow()
    db.add(video_details)
    db.commit()

    # Add missing fields expected by the controller
    result["video_id"] = video_id
    result["thumbnail_url"] = result["custom_thumbnail_path"]
    result["method_used"] = "generated_thumbnail"
    
    return result


async def update_thumbnail_service(video_id: str, user_id: UUID, db: Session) -> dict:
    """Update a thumbnail for a video"""
    # get customthumbail field  from db  and update yotube 
    statement = select(SingleVideoDetails).where(
        SingleVideoDetails.video_id == video_id,
        SingleVideoDetails.user_id == user_id
    )
    video_details = db.exec(statement).first()
    if not video_details:
        raise ValidationError(
            "Video not found in database for the current user", 
            field="video_id", 
            value=video_id, 
            error_type="video_not_found"
        )

    # create youtube client and upload to youtube 
    youtube_client = get_youtube_client(user_id, db)
    if not youtube_client:
        raise ValidationError(
            "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens.",
            field="user_id", 
            value=user_id, 
            error_type="youtube_client_not_found"
        )
    # Upload thumbnail to YouTube
    try:
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(video_details.custom_thumbnail_path, mimetype='image/png')
        youtube_client.thumbnails().set(
            videoId=video_id,
            media_body=media
        ).execute()
        logger.info(f"Successfully uploaded thumbnail to YouTube for video {video_id}")
    except Exception as e:
        logger.warning(f"Failed to upload thumbnail to YouTube for video {video_id}: {e}")
        # Don't raise error here - the local save was successful

    return {
        "success": True,
        "message": "Thumbnail updated successfully",
        "video_id": video_id,
        "thumbnail_url": video_details.custom_thumbnail_path,
        "method_used": "generated_thumbnail"
    }












# HELPERS

def _find_video_playlist(youtube_client, video_id: str) -> Optional[Dict[str, str]]:
    """
    Find which playlist a video actually belongs to by searching through user's playlists
    
    Args:
        youtube_client: Authenticated YouTube client
        video_id: YouTube video ID
        
    Returns:
        Dict with 'playlist_id' and 'playlist_name' if found, None if video is not in any playlist
    """
    try:
        # Get all playlists for the user
        playlists_response = youtube_client.playlists().list(
            part='snippet',
            mine=True,
            maxResults=50
        ).execute()
        
        # Search through each playlist to find the video
        for playlist in playlists_response.get('items', []):
            playlist_id = playlist['id']
            playlist_name = playlist['snippet']['title']
            
            try:
                # Check if video is in this playlist
                playlist_items = youtube_client.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    videoId=video_id,
                    maxResults=1
                ).execute()
                
                if playlist_items.get('items'):
                    logger.info(f"Found video {video_id} in playlist '{playlist_name}' ({playlist_id})")
                    return {
                        'playlist_id': playlist_id,
                        'playlist_name': playlist_name
                    }
                    
            except Exception as e:
                logger.warning(f"Error checking playlist {playlist_id}: {e}")
                continue
        
        # If not found in any playlist, check if it's in uploads playlist
        try:
            channel_response = youtube_client.channels().list(
                part='contentDetails',
                mine=True
            ).execute()
            
            if channel_response.get('items'):
                uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                # Check if video is in uploads playlist
                uploads_items = youtube_client.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    videoId=video_id,
                    maxResults=1
                ).execute()
                
                if uploads_items.get('items'):
                    logger.info(f"Video {video_id} found in uploads playlist ({uploads_playlist_id})")
                    return {
                        'playlist_id': uploads_playlist_id,
                        'playlist_name': 'Uploads'
                    }
                    
        except Exception as e:
            logger.warning(f"Error checking uploads playlist: {e}")
        
        logger.info(f"Video {video_id} not found in any playlist")
        return None
        
    except Exception as e:
        logger.error(f"Error finding playlist for video {video_id}: {e}")
        return None


def _fetch_from_youtube_api(video_id: str, user_id: UUID, db: Session) -> Dict[str, Any]:
    """Helper function to fetch video details from YouTube API"""
    logger.info(f"Attempting to get YouTube client for user_id: {user_id}")
    youtube_client = get_youtube_client(user_id, db)
    if not youtube_client:
        logger.error(f"Failed to get YouTube client for user_id: {user_id}")
        return {"error": "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens."}
    
    try:
        youtube_response = youtube_client.videos().list(
            part='snippet,status,statistics,contentDetails',
            id=video_id
        ).execute()
        
        if not youtube_response.get('items'):
            return {"error": "Video not found on YouTube"}
        
        youtube_video = youtube_response['items'][0]
        snippet = youtube_video.get('snippet', {})
        status = youtube_video.get('status', {})
        statistics = youtube_video.get('statistics', {})
        content_details = youtube_video.get('contentDetails', {})
        
        # Fetch transcript from YouTube with fallback system
        transcript_data = None
        # Try third-party transcript API first
        try:
            logger.info(f"Attempting to fetch transcript for video {video_id} using third-party API")
            transcript_result = _fetch_transcript_from_youtube(video_id)
            if transcript_result:
                # Convert to JSON string for storage
                transcript_data = json.dumps(transcript_result, ensure_ascii=False)
                logger.info(f"Successfully fetched transcript for video {video_id} using third-party API")
            else:
                logger.warning(f"No transcript available for video {video_id} using third-party API")
                # Trigger fallback when third-party API returns None
                raise Exception("Third-party API returned None")
        except Exception as e:
            logger.warning(f"Third-party transcript API failed for video {video_id}: {e}")
            
            # Fallback to official YouTube Captions API
            try:
                logger.info(f"Attempting to fetch captions for video {video_id} using official YouTube API")
                transcript_result = _fetch_captions_from_youtube_api(youtube_client, video_id)
                if transcript_result:
                    # Convert to JSON string for storage
                    transcript_data = json.dumps(transcript_result, ensure_ascii=False)
                    logger.info(f"Successfully fetched captions for video {video_id} using official YouTube API")
                else:
                    logger.warning(f"No captions available for video {video_id} using official YouTube API")
            except Exception as e2:
                logger.warning(f"Official YouTube Captions API also failed for video {video_id}: {e2}")
                # Both methods failed, continue without transcript

        # Calculate analytics fields
        from datetime import datetime
        import re
        
        # Extract published date
        published_at = None
        days_since_published = None
        views_per_day = None
        
        if snippet.get('publishedAt'):
            try:
                # Parse YouTube's ISO 8601 format: "2023-10-15T14:30:00Z"
                published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                
                # Calculate days since published
                now = datetime.now(published_at.tzinfo)
                days_since_published = (now - published_at).days
                
                # Calculate views per day (avoid division by zero)
                view_count = int(statistics.get('viewCount', 0))
                if days_since_published > 0 and view_count > 0:
                    views_per_day = round(view_count / days_since_published, 2)
                    
            except Exception as e:
                logger.warning(f"Error calculating analytics for video {video_id}: {e}")
        
        # Parse duration to get watch time (YouTube format: PT4M13S)
        watch_time_minutes = None
        if content_details.get('duration'):
            try:
                duration_str = content_details['duration']  # e.g., "PT4M13S"
                # Parse ISO 8601 duration format
                match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
                if match:
                    hours = int(match.group(1) or 0)
                    minutes = int(match.group(2) or 0)
                    seconds = int(match.group(3) or 0)
                    watch_time_minutes = round(hours * 60 + minutes + seconds / 60, 2)
            except Exception as e:
                logger.warning(f"Error parsing duration for video {video_id}: {e}")

        # Find which playlist this video actually belongs to
        playlist_info = _find_video_playlist(youtube_client, video_id)
        actual_playlist_id = playlist_info['playlist_id'] if playlist_info else None
        actual_playlist_name = playlist_info['playlist_name'] if playlist_info else None
        logger.info(f"Video {video_id} belongs to playlist: {actual_playlist_name} ({actual_playlist_id})")

        return {
            "title": snippet.get('title'),
            "description": snippet.get('description'),
            "thumbnail_url": snippet.get('thumbnails', {}).get('high', {}).get('url') or 
                           snippet.get('thumbnails', {}).get('medium', {}).get('url') or 
                           snippet.get('thumbnails', {}).get('default', {}).get('url'),
            "privacy_status": status.get('privacyStatus'),
            "playlist": actual_playlist_id,  # Store the actual playlist ID this video belongs to
            "playlist_name": actual_playlist_name,  # Store the playlist name
            "transcript": transcript_data,
            
            # Analytics fields
            "view_count": int(statistics.get('viewCount', 0)) if statistics.get('viewCount') else None,
            "like_count": int(statistics.get('likeCount', 0)) if statistics.get('likeCount') else None,
            "comment_count": int(statistics.get('commentCount', 0)) if statistics.get('commentCount') else None,
            "watch_time_minutes": watch_time_minutes,
            "published_at": published_at,
            "youtube_video_url": f"https://www.youtube.com/watch?v={video_id}",
            "days_since_published": days_since_published,
            "views_per_day": views_per_day
        }
    except Exception as e:
        return {"error": f"Error fetching from YouTube API: {str(e)}"}


def _save_to_database(video_id: str, youtube_data: Dict[str, Any], user_id: UUID, db: Session) -> SingleVideoDetails:
    """Helper function to save/update video details in database"""
    # Check if record exists for this user
    statement = select(SingleVideoDetails).where(
        SingleVideoDetails.video_id == video_id,
        SingleVideoDetails.user_id == user_id
    )
    video_details = db.exec(statement).first()
    
    if video_details:
        # Update existing record
        video_details.title = youtube_data["title"]
        video_details.description = youtube_data["description"]
        video_details.thumbnail_link = youtube_data["thumbnail_url"]
        video_details.privacy_status = youtube_data["privacy_status"]
        video_details.playlist = youtube_data.get("playlist")
        video_details.playlist_name = youtube_data.get("playlist_name")
        video_details.transcript = youtube_data.get("transcript")
        
        # Update analytics fields
        video_details.view_count = youtube_data.get("view_count")
        video_details.like_count = youtube_data.get("like_count")
        video_details.comment_count = youtube_data.get("comment_count")
        video_details.watch_time_minutes = youtube_data.get("watch_time_minutes")
        video_details.published_at = youtube_data.get("published_at")
        video_details.youtube_video_url = youtube_data.get("youtube_video_url")
        video_details.days_since_published = youtube_data.get("days_since_published")
        video_details.views_per_day = youtube_data.get("views_per_day")
        
        video_details.updated_at = datetime.utcnow()
    else:
        # Create new record
        video_details = SingleVideoDetails(
            video_id=video_id,
            user_id=user_id,
            title=youtube_data["title"],
            description=youtube_data["description"],
            thumbnail_link=youtube_data["thumbnail_url"],
            privacy_status=youtube_data["privacy_status"],
            playlist=youtube_data.get("playlist"),
            playlist_name=youtube_data.get("playlist_name"),
            transcript=youtube_data.get("transcript"),
            
            # Analytics fields
            view_count=youtube_data.get("view_count"),
            like_count=youtube_data.get("like_count"),
            comment_count=youtube_data.get("comment_count"),
            watch_time_minutes=youtube_data.get("watch_time_minutes"),
            published_at=youtube_data.get("published_at"),
            youtube_video_url=youtube_data.get("youtube_video_url"),
            days_since_published=youtube_data.get("days_since_published"),
            views_per_day=youtube_data.get("views_per_day")
        )
    
    db.add(video_details)
    db.commit()
    db.refresh(video_details)
    return video_details
