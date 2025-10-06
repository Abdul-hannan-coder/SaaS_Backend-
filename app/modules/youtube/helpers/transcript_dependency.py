from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlmodel import Session, select
import json
from datetime import datetime
from ..video.model import Video
from ..dashboard_single_video.model import SingleVideoDetails
from .youtube_client import get_youtube_client
from ....utils.my_logger import get_logger

# Try to import youtube-transcript-api
try:
    from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YouTubeTranscriptApi = None  # type: ignore
    YOUTUBE_TRANSCRIPT_AVAILABLE = False

logger = get_logger("TRANSCRIPT_DEPENDENCY")


def _fetch_transcript_from_youtube(youtube_video_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch transcript from YouTube using youtube-transcript-api
    
    Args:
        youtube_video_id: The YouTube video ID (not database UUID)
        
    Returns:
        Formatted transcript data or None if not available
    """
    if not YOUTUBE_TRANSCRIPT_AVAILABLE or YouTubeTranscriptApi is None:
        logger.error("youtube-transcript-api not available. Cannot fetch transcript from YouTube.")
        return None
    
    try:
        logger.info(f"Fetching transcript from YouTube for video: {youtube_video_id}")
        
        # Get transcript from YouTube in any available language
        api = YouTubeTranscriptApi()
        
        # First, get list of available transcripts
        transcript_list_obj = api.list(youtube_video_id)
        
        # Try to get any available transcript (auto-generated or manual)
        transcript_result = transcript_list_obj.find_transcript(['en', 'hi', 'es', 'fr', 'de', 'ar', 'ja', 'ko', 'zh'])
        
        if not transcript_result:
            # If specific languages don't work, try to get any available transcript
            available_transcripts = list(transcript_list_obj)
            if available_transcripts:
                transcript_result = available_transcripts[0]  # Get first available transcript
            else:
                logger.warning(f"No transcript found for video {youtube_video_id}")
                return None
        
        # Fetch the actual transcript data
        transcript_list = transcript_result.fetch()
        used_language = transcript_result.language_code
        logger.info(f"Successfully fetched transcript in language: {used_language}")
        
        # Convert to our format
        segments = []
        for entry in transcript_list:
            # Handle both dict format and FetchedTranscriptSnippet objects
            if hasattr(entry, 'start'):
                # FetchedTranscriptSnippet object
                start_time = entry.start
                text = entry.text
            else:
                # Dict format
                start_time = entry['start']
                text = entry['text']
            
            # Convert seconds to MM:SS format
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"{minutes:02d}:{seconds:02d}"
            
            segments.append({
                "timestamp": timestamp,
                "text": text.strip()
            })
        
        transcript_data = {
            "segments": segments,
            "source": "youtube",
            "language": used_language,
            "fetched_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Successfully fetched transcript from YouTube: {len(segments)} segments")
        return transcript_data
        
    except Exception as e:
        logger.error(f"Error fetching transcript from YouTube for video {youtube_video_id}: {e}")
        return None


def _save_transcript_to_db(video_id: UUID, user_id: UUID, transcript_data: Dict[str, Any], db: Session) -> bool:
    """
    Save transcript to database for a video
    
    Args:
        video_id: Database video UUID
        user_id: User UUID
        transcript_data: Transcript data to save
        db: Database session
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Try to find in Video table first
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if video:
            video.transcript = json.dumps(transcript_data, ensure_ascii=False)
            db.add(video)
            db.commit()
            logger.info(f"Transcript saved to Video table for video {video_id}")
            return True
        
        logger.warning(f"Video {video_id} not found in database for transcript saving")
        return False
        
    except Exception as e:
        logger.error(f"Error saving transcript to database: {e}")
        return False


def get_video_transcript(video_id: UUID, user_id: UUID, db: Session, youtube_video_id: Optional[str] = None) -> Optional[str]:
    """
    Get the transcript for a specific video.
    First checks database, then fetches from YouTube if not found.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        youtube_video_id: Optional YouTube video ID for fetching from YouTube
        
    Returns:
        The transcript as a string, or None if not found/not authorized
    """
    try:
        logger.info(f"Fetching transcript for video {video_id} by user {user_id}")
        
        # Step 1: Check database first
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            logger.warning(f"Video {video_id} not found for user {user_id}")
            return None
        
        # If transcript exists in database, return it
        if video.transcript:
            logger.info(f"Transcript retrieved from database for video {video_id}")
            return video.transcript
        
        # Step 2: If no transcript in database, try to fetch from YouTube
        if youtube_video_id:
            logger.info(f"No transcript in database, attempting to fetch from YouTube for video {youtube_video_id}")
            
            transcript_data = _fetch_transcript_from_youtube(youtube_video_id)
            if transcript_data:
                # Save to database for future use
                transcript_json = json.dumps(transcript_data, ensure_ascii=False)
                video.transcript = transcript_json
                db.add(video)
                db.commit()
                
                logger.info(f"Transcript fetched from YouTube and saved to database for video {video_id}")
                return transcript_json
            else:
                logger.warning(f"Could not fetch transcript from YouTube for video {youtube_video_id}")
        else:
            logger.warning(f"No YouTube video ID provided, cannot fetch from YouTube for video {video_id}")
        
        logger.warning(f"No transcript available for video {video_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching transcript for video {video_id}: {e}")
        return None

def get_video_transcript_parsed(video_id: UUID, user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get the transcript for a video and parse it as JSON.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        Parsed transcript as a dictionary, or None if not found/invalid
    """
    try:
        transcript_json = get_video_transcript(video_id, user_id, db)
        
        if not transcript_json:
            return None
        
        # Parse the JSON transcript
        transcript_data = json.loads(transcript_json)
        
        logger.info(f"Transcript parsed successfully for video {video_id}")
        return transcript_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing transcript JSON for video {video_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting parsed transcript for video {video_id}: {e}")
        return None

def get_video_transcript_text_only(video_id: UUID, user_id: UUID, db: Session) -> Optional[str]:
    """
    Get the transcript text only (without timestamps) for a video.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        Plain text transcript, or None if not found
    """
    try:
        transcript_data = get_video_transcript_parsed(video_id, user_id, db)
        
        if not transcript_data:
            return None
        
        # Extract text from segments
        segments = transcript_data.get('segments', [])
        text_parts = []
        
        for segment in segments:
            if isinstance(segment, dict) and 'text' in segment:
                text_parts.append(segment['text'])
        
        full_text = ' '.join(text_parts)
        
        logger.info(f"Text-only transcript extracted for video {video_id}")
        return full_text
        
    except Exception as e:
        logger.error(f"Error extracting text-only transcript for video {video_id}: {e}")
        return None

def get_video_transcript_segments(video_id: UUID, user_id: UUID, db: Session) -> Optional[List[Dict[str, str]]]:
    """
    Get the transcript segments with timestamps for a video.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        List of segments with timestamps and text, or None if not found
    """
    try:
        transcript_data = get_video_transcript_parsed(video_id, user_id, db)
        
        if not transcript_data:
            return None
        
        segments = transcript_data.get('segments', [])
        
        logger.info(f"Transcript segments retrieved for video {video_id}")
        return segments
        
    except Exception as e:
        logger.error(f"Error getting transcript segments for video {video_id}: {e}")
        return None

def check_transcript_availability(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Check if a transcript is available for a video.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        Dictionary with availability status and metadata
    """
    try:
        logger.info(f"Checking transcript availability for video {video_id}")
        
        # Get video
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            return {
                "available": False,
                "reason": "Video not found or not authorized",
                "has_transcript": False,
                "transcript_length": 0
            }
        
        if not video.transcript:
            return {
                "available": False,
                "reason": "No transcript available",
                "has_transcript": False,
                "transcript_length": 0
            }
        
        # Try to parse transcript to get more info
        try:
            transcript_data = json.loads(video.transcript)
            segments = transcript_data.get('segments', [])
            text_parts = [seg.get('text', '') for seg in segments if isinstance(seg, dict)]
            full_text = ' '.join(text_parts)
            
            return {
                "available": True,
                "reason": "Transcript available",
                "has_transcript": True,
                "transcript_length": len(full_text),
                "segment_count": len(segments),
                "first_segment": segments[0] if segments else None,
                "last_segment": segments[-1] if segments else None
            }
            
        except json.JSONDecodeError:
            return {
                "available": False,
                "reason": "Invalid transcript format",
                "has_transcript": True,
                "transcript_length": len(video.transcript)
            }
        
    except Exception as e:
        logger.error(f"Error checking transcript availability for video {video_id}: {e}")
        return {
            "available": False,
            "reason": f"Error: {str(e)}",
            "has_transcript": False,
            "transcript_length": 0
        }

def get_transcript_for_ai_processing(video_id: UUID, user_id: UUID, db: Session) -> Optional[str]:
    """
    Get transcript optimized for AI processing (cleaned and formatted).
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        Cleaned transcript text optimized for AI processing
    """
    try:
        transcript_text = get_video_transcript_text_only(video_id, user_id, db)
        
        if not transcript_text:
            return None
        
        # Clean the transcript for AI processing
        cleaned_text = transcript_text.strip()
        
        # Remove extra whitespace
        cleaned_text = ' '.join(cleaned_text.split())
        
        # Basic cleaning for better AI processing
        cleaned_text = cleaned_text.replace('  ', ' ')  # Remove double spaces
        
        logger.info(f"Transcript prepared for AI processing for video {video_id}")
        return cleaned_text
        
    except Exception as e:
        logger.error(f"Error preparing transcript for AI processing for video {video_id}: {e}")
        return None


def get_youtube_video_transcript(youtube_video_id: str, user_id: UUID, db: Session) -> Optional[str]:
    """
    Get transcript for a YouTube video by its YouTube ID.
    First checks if we have it cached in single_video_details, then fetches from YouTube.
    
    Args:
        youtube_video_id: The YouTube video ID (e.g., "ngYXsg4z8K8")
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        The transcript as a JSON string, or None if not found
    """
    try:
        logger.info(f"Fetching transcript for YouTube video {youtube_video_id} by user {user_id}")
        
        # Step 1: Check if we have this video in single_video_details
        statement = select(SingleVideoDetails).where(
            SingleVideoDetails.video_id == youtube_video_id,
            SingleVideoDetails.user_id == user_id
        )
        video_details = db.exec(statement).first()
        
        # For now, we don't store transcripts in single_video_details
        # So we'll directly fetch from YouTube
        
        # Step 2: Fetch from YouTube
        logger.info(f"Attempting to fetch transcript from YouTube for video {youtube_video_id}")
        
        transcript_data = _fetch_transcript_from_youtube(youtube_video_id)
        if transcript_data:
            transcript_json = json.dumps(transcript_data, ensure_ascii=False)
            logger.info(f"Transcript fetched from YouTube for video {youtube_video_id}")
            return transcript_json
        else:
            logger.warning(f"Could not fetch transcript from YouTube for video {youtube_video_id}")
            return None
        
    except Exception as e:
        logger.error(f"Error fetching transcript for YouTube video {youtube_video_id}: {e}")
        return None