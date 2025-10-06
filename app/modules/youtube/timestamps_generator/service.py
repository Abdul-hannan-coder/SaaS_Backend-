from agents import Agent, Runner, AgentOutputSchema, set_tracing_disabled ,OpenAIChatCompletionsModel,AsyncOpenAI
from agents.extensions.models.litellm_model import LitellmModel, ModelSettings
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
import re
from datetime import datetime, timedelta
import asyncio
import json
from sqlmodel import Session, select
from uuid import UUID

from ..video.model import Video
from .error_models import (
    TimestampsGenerationError,
    TimestampsSaveError,
    VideoNotFoundError,
    VideoTranscriptNotFoundError,
    ApiKeyMissingError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger
from ..helpers.transcript_dependency import get_video_transcript
from ..gemini.service import get_user_gemini_api_key

load_dotenv()
set_tracing_disabled(True)
logger = get_logger("TIMESTAMPS_GENERATOR_SERVICE")

# model = LitellmModel(
#     model="gemini/gemini-2.0-flash",
#     api_key="AIzaSyBf-7p-DiTq3s1rLwwnC_jaXVWEK8naVjE",
# )

class TimeStampsGeneratorOutput(BaseModel):
            timestamps: list[str] = Field(
                description="List of timestamps in format 'MM:SS Topic Name' (e.g., '00:00 Introduction', '01:30 Main Topic')",
                examples=[
                    ["00:00 Introduction", "01:30 Main Topic", "03:45 Conclusion"]
                ]
            )





# Core service functions with proper error handling

async def generate_video_timestamps(
    video_id: UUID, 
    user_id: UUID, 
    db: Session
) -> dict:
    """
    Generate timestamps for a video using its transcript
    """
    # Validate API key
    api_key = get_user_gemini_api_key(user_id, db)
    if not api_key:
        raise ApiKeyMissingError("Gemini API key is required for timestamps generation", user_id=str(user_id))
    
    # Get video transcript
    transcript = get_video_transcript(video_id, user_id, db)
    if not transcript:
        raise VideoTranscriptNotFoundError("Video transcript not found or not generated yet", video_id=str(video_id), user_id=str(user_id))
    
    # Generate timestamps
    try:
        timestamps = await _time_stamps_generator(transcript, api_key)
        
        if not timestamps or not timestamps.strip():
            raise TimestampsGenerationError("Failed to generate timestamps", video_id=str(video_id), user_id=str(user_id))
        
        logger.info(f"Timestamps generated successfully for video {video_id}")
        
        return {
            "success": True,
            "message": "Timestamps generated successfully",
            "video_id": str(video_id),
            "generated_timestamps": timestamps.strip()
        }
        
    except Exception as e:
        raise TimestampsGenerationError(f"Error generating timestamps: {str(e)}", video_id=str(video_id), user_id=str(user_id))


async def save_video_timestamps(
    video_id: UUID,
    user_id: UUID,
    timestamps: str,
    db: Session
) -> dict:
    """
    Save the timestamps to the video record
    """
    # Validate timestamps
    if not timestamps or not timestamps.strip():
        raise ValidationError("Timestamps cannot be empty", field="timestamps", error_type="missing_field")
    
    if len(timestamps.strip()) < 10:
        raise ValidationError("Timestamps must be at least 10 characters long", field="timestamps", error_type="too_short")
    
    if len(timestamps.strip()) > 10000:
        raise ValidationError("Timestamps must be less than 10000 characters", field="timestamps", error_type="too_long")
    
    # Check if video exists
    statement = select(Video).where(
        Video.id == video_id,
        Video.user_id == user_id
    )
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found", video_id=str(video_id), user_id=str(user_id))
    
    # Database operations
    try:
        video.timestamps = timestamps.strip()
        db.add(video)
        db.commit()
        
        logger.info(f"Timestamps saved successfully for video {video_id}")
        
        return {
            "success": True,
            "message": "Timestamps saved successfully",
            "video_id": str(video_id),
            "timestamps": timestamps.strip()
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error saving timestamps: {str(e)}", operation="save_video_timestamps", error_type="transaction")


async def regenerate_video_timestamps(
    video_id: UUID,
    user_id: UUID,
    db: Session
) -> dict:
    """
    Regenerate timestamps for a video using its transcript
    """
    # Validate API key
    api_key = get_user_gemini_api_key(user_id, db)
    if not api_key:
        raise ApiKeyMissingError("Gemini API key is required for timestamps regeneration", user_id=str(user_id))
    
    # Get video transcript
    transcript = get_video_transcript(video_id, user_id, db)
    if not transcript:
        raise VideoTranscriptNotFoundError("Video transcript not found or not generated yet", video_id=str(video_id), user_id=str(user_id))
    
    # Check if video exists
    statement = select(Video).where(
        Video.id == video_id,
        Video.user_id == user_id
    )
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found", video_id=str(video_id), user_id=str(user_id))
    
    # Generate new timestamps
    try:
        timestamps = await _time_stamps_generator(transcript, api_key)
        
        if not timestamps or not timestamps.strip():
            raise TimestampsGenerationError("Failed to regenerate timestamps", video_id=str(video_id), user_id=str(user_id))
        
        # Save new timestamps to database
        video.timestamps = timestamps.strip()
        db.add(video)
        db.commit()
        
        logger.info(f"Timestamps regenerated successfully for video {video_id}")
        
        return {
            "success": True,
            "message": "Timestamps regenerated successfully",
            "video_id": str(video_id),
            "generated_timestamps": timestamps.strip()
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error regenerating timestamps: {str(e)}", operation="regenerate_video_timestamps", error_type="transaction")




# ======================================
# ======================================

# Helper functions


# ======================================
# ======================================


def _validate_and_fix_timestamps(timestamps_text: str) -> str:
    """
    Validate and fix timestamps to ensure they are in proper MM:SS format.
    
    Args:
        timestamps_text (str): Raw timestamps text from agent
    
    Returns:
        str: Fixed timestamps text
    """
    # Extract timestamps using regex
    timestamp_pattern = r'(\d{1,2}):(\d{1,2})'
    
    def fix_timestamp(match):
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        
        # Fix invalid seconds (should be 0-59)
        if seconds >= 60:
            minutes += seconds // 60
            seconds = seconds % 60
        
        # Ensure minutes don't exceed reasonable limits (e.g., 999)
        if minutes > 999:
            minutes = 999
        
        # Format as MM:SS
        return f"{minutes:02d}:{seconds:02d}"
    
    # Fix all timestamps in the text
    fixed_text = re.sub(timestamp_pattern, fix_timestamp, timestamps_text)
    
    return fixed_text

async def _time_stamps_generator(transcript: str, api_key: str) -> str:
    """
    Generate timestamps from video transcript using multiple models with retry logic
    """
    
    # Define models to try in order (Pollinations first, then Gemini, then other fallbacks)
    models_to_try = []
    
    # Primary models: Try Pollinations models first
    models_to_try.extend([
        {
            "name": "OpenAI Reasoning (Pollinations)", 
            "model": OpenAIChatCompletionsModel(
                model="openai-reasoning",
                openai_client=AsyncOpenAI(
                    api_key="L3g92SSpMD_I6mnr",
                    base_url="https://text.pollinations.ai/openai",
                )
            )
        },
        {
            "name": "OpenAI Large (Pollinations)",
            "model": OpenAIChatCompletionsModel(
                model="openai-large", 
                openai_client=AsyncOpenAI(
                    api_key="L3g92SSpMD_I6mnr",
                    base_url="https://text.pollinations.ai/openai",
                )
            )
        }
    ])
    
    # Secondary fallback: Gemini API (if API key provided)
    if api_key:
        models_to_try.append({
            "name": "Gemini 2.0 Flash",
            "model": OpenAIChatCompletionsModel(
                openai_client=AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                ),
                model="gemini-2.0-flash",
            )
        })
    
    # Final fallback models: Other Pollinations models
    models_to_try.extend([
        {
            "name": "Artist Model (Pollinations)",
            "model": OpenAIChatCompletionsModel(
                model="rtist",
                openai_client=AsyncOpenAI(
                    api_key="L3g92SSpMD_I6mnr", 
                    base_url="https://text.pollinations.ai/openai",
                )
            )
        },
        {
            "name": "Bidara Model (Pollinations)",
            "model": OpenAIChatCompletionsModel(
                model="bidara",
                openai_client=AsyncOpenAI(
                    api_key="L3g92SSpMD_I6mnr",
                    base_url="https://text.pollinations.ai/openai", 
                )
            )
        }
    ])
    
    # Prepare the prompt
    prompt = "Generate timestamps for the youtube video. Create important chapters only, start with 00:00, and ensure all timestamps are in MM:SS format with seconds 0-59: " + transcript
    
    # Try each model with retry logic
    for attempt, model_config in enumerate(models_to_try):
        try:
            logger.info(f"🔄 Attempting timestamps generation with {model_config['name']} (attempt {attempt + 1}/{len(models_to_try)})")
            
            agent = Agent(
                model=model_config["model"],
                model_settings=ModelSettings(
                    temperature=0.3,
                ),
                name="YouTube Video Time Stamps Generator",
                instructions="""Your job is to generate time stamps for a youtube video based on its transcript
                in english create chapters for the video for example discussion , topic start, topic end  example , discussion , introduction , conclusion , etc.
                
                You should generate time stamps in the following format:
                - Each timestamp should be a string in format: "MM:SS Topic Name"
                - Example: "00:00 Introduction", "01:30 Main Topic", "03:45 Conclusion"
                
                # 🧠 Rules for YouTube Chapters to Work:
                
                    1. Must start with 00:00

                    2. Each timestamp must be followed by a space and then a title

                    3. There must be at least 3 timestamps

                    4. Each timestamp must be chronologically increasing

                    5. dont create too many chapters just important and bigger chapters

                    6. dont create chapters that are too short like 00:01 , 00:02 , 00:03 , etc.

                    7. IMPORTANT: Seconds must be between 00-59 (never 60 or higher)
                    Examples: 00:00, 00:30, 01:00, 01:45, 02:30 (✅ CORRECT)
                    Examples: 00:60, 01:78, 02:99 (❌ WRONG - seconds > 59)

                    8. Minutes can be any number but seconds must be 0-59

                    9. Format must be MM:SS where MM = minutes, SS = seconds (0-59)

                    10. Return as a list of strings, not a dictionary

                """,
                output_type=TimeStampsGeneratorOutput,
            )
            
            result = await Runner.run(
                agent,
                input=prompt,
            )
            
            # Get the structured output
            output = result.final_output
            
            # Validate and fix each timestamp
            fixed_timestamps = []
            for timestamp_entry in output.timestamps:
                # Extract the timestamp part (before the first space)
                parts = timestamp_entry.split(' ', 1)
                if len(parts) >= 2:
                    timestamp = parts[0]
                    topic = parts[1]
                    fixed_timestamp = _validate_and_fix_timestamps(timestamp)
                    fixed_timestamps.append(f"{fixed_timestamp} {topic}")
                else:
                    # If no space found, just fix the timestamp
                    fixed_timestamps.append(_validate_and_fix_timestamps(timestamp_entry))
            
            # Join with newlines
            timestamps_result = "\n".join(fixed_timestamps)
            
            logger.info(f"✅ Timestamps generation successful with {model_config['name']}")
            return timestamps_result
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"⚠️ Timestamps generation failed with {model_config['name']}: {error_msg}")
            
            # If this is not the last model, continue to next one
            if attempt < len(models_to_try) - 1:
                logger.info(f"🔄 Trying next model...")
                # Optional: Add a small delay between retries
                await asyncio.sleep(1)
                continue
            else:
                # This was the last model, raise the error
                logger.error(f"❌ All {len(models_to_try)} models failed for timestamps generation")
                raise TimestampsGenerationError(f"Timestamps generation failed with all models. Last error: {error_msg}")
    
    # This should never be reached, but just in case
    raise TimestampsGenerationError("Timestamps generation failed: No models available")
