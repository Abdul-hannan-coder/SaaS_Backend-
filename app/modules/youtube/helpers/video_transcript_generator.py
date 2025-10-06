from pydantic import BaseModel, Field
import json
from google import genai
import subprocess
import os
import shutil
import time
from pathlib import Path
from sqlmodel import Session, select
from uuid import UUID
from ....utils.my_logger import get_logger
from .ffmpeg_finder import find_ffmpeg, test_ffmpeg
from ..video.model import Video  
logger = get_logger("VIDEO_TRANSCRIPT_GENERATOR")


class TranscriptSegment(BaseModel):
    timestamp: str = Field(description="Timestamp in MM:SS format (e.g., '00:00', '01:30')")
    text: str = Field(description="The transcript text for this segment")

class TranscriptOutput(BaseModel):
    segments: list[TranscriptSegment] = Field(
        description="List of transcript segments with timestamps"
    )



def generate_video_transcript(video_path: str) -> TranscriptOutput:
    """
    Extract audio from video and generate transcript using Google GenAI API.
    Automatically cleans up the temporary audio file after transcript generation.
    
    Args:
        video_path (str): Path to input video file
        
    Returns:
        TranscriptOutput: Generated transcript with timestamps
    """
 

    # Generate temporary audio path
    audio_path = str(Path(video_path).with_suffix('.mp3'))

    try:
        # Get ffmpeg path using comprehensive finder
        logger.info("🔍 Locating ffmpeg executable...")
        ffmpeg_path = find_ffmpeg()
        
        # Test if ffmpeg is working
        if not test_ffmpeg(ffmpeg_path):
            raise Exception("ffmpeg found but not working properly")
        
        # First, check if the video has audio streams using ffprobe
        probe_cmd = [
            ffmpeg_path.replace('ffmpeg', 'ffprobe'),  # Use ffprobe for better stream analysis
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            video_path
        ]
        
        logger.info(f"🔍 Checking for audio streams in video...")
        try:
            probe_result = subprocess.run(probe_cmd, check=True, capture_output=True, text=True)
            probe_data = json.loads(probe_result.stdout)
            
            # Check if there are any audio streams
            has_audio = False
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    has_audio = True
                    logger.info(f"✅ Found audio stream: {stream.get('codec_name', 'unknown')} codec")
                    break
            
            if not has_audio:
                logger.warning(f"⚠️ No audio streams found in video: {video_path}")
                raise Exception("Video does not contain audio streams. Transcript generation requires audio content.")
                
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️ Could not analyze video streams, proceeding with audio extraction: {e}")
            # If ffprobe fails, we'll let the audio extraction attempt proceed
            # and handle the error there
        
        # Extract audio using ffmpeg
        cmd = [
            ffmpeg_path,
            '-i', video_path,  # Input file
            '-q:a', '0',       # Highest quality
            '-map', 'a',       # Extract audio only
            '-y',              # Overwrite output file if exists
            audio_path
        ]
        
        logger.info(f"🎬 Running ffmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"✅ Audio extracted successfully to: {audio_path}")

        # Generate transcript with retry logic
        client = genai.Client()
        myfile = client.files.upload(file=audio_path)
        
        prompt = """
        Generate a detailed transcript of this audio clip with timestamps.
        
        Return the response in the following JSON format:
        {
            "segments": [
                {
                    "timestamp": "MM:SS",
                    "text": "transcript text for this segment"
                }
            ]
        }
        
        Rules:
        1. Start with timestamp "00:00"
        3. Timestamps must be in MM:SS format with seconds 0-59
        4. Include all spoken content accurately
        5. Maintain chronological order
        6. Each segment should contain complete thoughts or sentences
        """
        
        # Retry logic: 3 attempts with 1-minute delays
        max_retries = 3
        retry_delay = 60  # 1 minute in seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Attempting transcript generation (attempt {attempt + 1}/{max_retries})")
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[prompt, myfile],
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": TranscriptOutput.model_json_schema(),
                    }
                )
                
                # If we get here, the request was successful
                logger.info("✅ Transcript generated successfully")
                break
                
            except Exception as api_error:
                error_str = str(api_error)
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {error_str}")
                
                # Check if it's a 503 UNAVAILABLE error or similar overload error
                if "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower():
                    if attempt < max_retries - 1:  # Don't wait after the last attempt
                        logger.info(f"🕐 Model overloaded, waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"❌ All {max_retries} attempts failed due to model overload")
                        raise Exception(f"Transcript generation failed after {max_retries} attempts: {error_str}")
                else:
                    # For non-503 errors, don't retry
                    logger.error(f"❌ Non-retryable error occurred: {error_str}")
                    raise Exception(f"Transcript generation failed: {error_str}")
        else:
            # This else clause runs if the for loop completes without breaking
            raise Exception(f"Transcript generation failed after {max_retries} attempts")
        
        # Parse response and clean up audio file
        transcript_data = json.loads(response.text)
        os.remove(audio_path)
        logger.info(f"🗑️ Temporary audio file removed: {audio_path}")
        
        return TranscriptOutput(**transcript_data)
        
    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Error extracting audio: {e.stderr if e.stderr else str(e)}"
        logger.error(error_msg)
        
        # Check if the error is due to missing audio streams
        if "Stream map 'a' matches no streams" in str(e.stderr):
            error_msg = "Video does not contain audio streams. Transcript generation requires audio content."
            logger.warning(f"⚠️ {error_msg}")
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"❌ Error in transcript generation: {e}"
        logger.error(error_msg)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        raise Exception(error_msg)





async def generate_transcript_background(video_id: UUID, video_path: str, db: Session):
    """
    Background task to generate transcript for a video
    """
    try:
        logger.info(f"Starting background transcript generation for video: {video_path}")
        transcript_output = generate_video_transcript(video_path)
        transcript_json = transcript_output.model_dump_json()
        
        # Update the video record with transcript
        statement = select(Video).where(Video.id == video_id)
        video = db.exec(statement).first()
        if video:
            video.transcript = transcript_json
            db.add(video)
            db.commit()
            logger.info(f"Transcript generated and stored successfully for video: {video_path}")
        else:
            logger.error(f"Video not found for transcript update: {video_id}")
            
    except Exception as e:
        error_msg = str(e)
        if "does not contain audio streams" in error_msg:
            logger.warning(f"⚠️ Skipping transcript generation for video {video_path}: {error_msg}")
            # Update video record to indicate no transcript available
            statement = select(Video).where(Video.id == video_id)
            video = db.exec(statement).first()
            if video:
                video.transcript = json.dumps({"error": "No audio streams found", "message": error_msg})
                db.add(video)
                db.commit()
                logger.info(f"Updated video record to indicate no transcript available: {video_path}")
        else:
            logger.error(f"Failed to generate transcript for video {video_path}: {e}")