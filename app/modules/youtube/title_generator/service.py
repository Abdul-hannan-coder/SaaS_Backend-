"""
Title generator service - handles all database operations and business logic
"""
import json
import re
import time
import asyncio
from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from agents import Agent, Runner, set_tracing_disabled, SQLiteSession
from agents.extensions.models.litellm_model import LitellmModel, ModelSettings
from dotenv import load_dotenv
import os
from agents import Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel, AsyncOpenAI

from ..video.model import Video

from .error_models import (
    TitleGenerationError,
    VideoNotFoundError,
    VideoTranscriptNotFoundError,
    ApiKeyMissingError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger
from ..helpers.transcript_dependency import get_video_transcript

logger = get_logger("TITLE_GENERATOR_SERVICE")

# Initialize agents session

load_dotenv()

class TitleRequest(BaseModel):
    video_id: UUID
    user_requirements: Optional[str] = None

class TitleResponse(BaseModel):
    video_id: UUID
    generated_titles: List[str]
    success: bool
    message: str

class TitleUpdateRequest(BaseModel):
    video_id: UUID
    title: str





async def generate_video_title(video_id: UUID, user_id: UUID, db: Session, user_requirements: Optional[str] = None, selected_title: Optional[str] = None, api_key: Optional[str] = None) -> TitleResponse:
    """
    Generate title for a video using its transcript
    """
    # Validate API key
    if not api_key:
        raise ApiKeyMissingError("Gemini API key is required for title generation", user_id=str(user_id))
    
    # Get video transcript
    transcript = get_video_transcript(video_id, user_id, db)
    
    if not transcript:
        raise VideoTranscriptNotFoundError("Video transcript not found or not generated yet", video_id=str(video_id), user_id=str(user_id))
    
    # Use transcript as is (JSON format)
    transcript_text = transcript
    
    # Use selected_title as user_requirements if provided and no user_requirements
    if selected_title and not user_requirements:
        user_requirements = selected_title
    
    # Generate titles
    title_output = await _generate_title_from_transcript(transcript_text, user_requirements, api_key)
    
    return TitleResponse(
        video_id=video_id,
        generated_titles=title_output.titles,
        success=True,
        message="Titles generated successfully"
    )

async def update_video_title(video_id: UUID, user_id: UUID, title: str, db: Session) -> dict:
    """
    Update video title in database
    """
    # Validate title
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty", field="title", error_type="missing_field")
    
    if len(title.strip()) < 3:
        raise ValidationError("Title must be at least 3 characters long", field="title", error_type="too_short")
    
    if len(title.strip()) > 200:
        raise ValidationError("Title must be less than 200 characters", field="title", error_type="too_long")
    
    # Check if title looks like a UUID (which would be wrong)
    if len(title.strip()) == 36 and title.strip().count('-') == 4:
        raise ValidationError("Title appears to be a UUID - please provide the actual title text", field="title", error_type="invalid_title")
    
    statement = select(Video).where(
        Video.id == video_id,
        Video.user_id == user_id
    )
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found", video_id=str(video_id), user_id=str(user_id))
    
    # Database operations
    try:
        video.title = title.strip()
        db.add(video)
        db.commit()
        
        logger.info(f"Title updated for video {video_id}: {title}")
        
        return {
            "success": True,
            "message": "Title updated successfully",
            "video_id": str(video_id),
            "title": title.strip()
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error updating video title: {str(e)}", operation="update_video_title", error_type="transaction")

async def regenerate_title(video_id: UUID, user_id: UUID, db: Session, selected_title: Optional[str] = None) -> TitleResponse:
    """
    Regenerate title for a video
    """
    return await generate_video_title(video_id, user_id, db, user_requirements=selected_title)




# ======================================
# ======================================

# Helper functions


# ======================================
# ======================================


class TitleGeneratorOutput(BaseModel):
    titles: List[str] = Field(..., description="List of 10 eye-catching YouTube titles")

async def _generate_title_from_transcript(transcript: str, user_requirements: Optional[str] = None, api_key: Optional[str] = None) -> TitleGeneratorOutput:
    """
    Generate a title from video transcript using the agents library with retry logic
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
            "model": LitellmModel(
                model="gemini/gemini-2.0-flash",
                api_key=api_key,
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
    if user_requirements:
        prompt = f"Generate the title of the YouTube video for the following transcript: {transcript}\n\nAdditional requirements: {user_requirements}"
    else:
        prompt = f"Generate the title of the YouTube video for the following transcript: {transcript}"
    
    # Try each model with retry logic
    for attempt, model_config in enumerate(models_to_try):
        try:
            logger.info(f"🔄 Attempting title generation with {model_config['name']} (attempt {attempt + 1}/{len(models_to_try)})")
            
            agent = Agent(
                name="YouTube Title Generator",
                model_settings=ModelSettings(
                    temperature=0.5,
                ),
                instructions="""You are a YouTube title generator specialized in creating engaging titles for educational and lecture-style content. You are given a transcript of a YouTube video and you need to generate 10 eye-catching titles that will attract viewers interested in learning.

        # IMPORTANT REQUIREMENTS:
        1. Generate exactly 10 different eye-catching YouTube titles
        2. Each title should be in English language only
        3. Each title should be less than 80 characters
        4. Make titles engaging, clickable, and optimized for YouTube's algorithm
        5. Use different styles: educational, curiosity-driven, problem-solving, skill-building, etc.
        6. Focus on the main topics and learning outcomes from the video
        7. Include relevant keywords, trending terms, and educational markers (e.g. "Tutorial", "Guide", "Masterclass")
        8. Make titles that signal clear value and learning benefits to viewers
        9. Vary the format: some with emojis (📚, ✨, 🎓), some with numbers, some questions, some statements
        10. Ensure each title is unique and different from the others
        11. Emphasize the educational/instructional nature of the content
        12. Use power words that resonate with learners: "Master", "Learn", "Understand", "Discover"
        13. Include skill level indicators where relevant (Beginner, Advanced, etc.)
        14. Consider adding time-saving or efficiency claims when appropriate
        15. Incorporate social proof elements ("Expert Shows", "Professor Explains")

        Generate 10 unique, education-focused titles that will attract viewers seeking quality learning content.
        """,
                model=model_config["model"],
                output_type=TitleGeneratorOutput,
            )
            
            result = await Runner.run(
                agent,
                input=prompt,
            )
            
            logger.info(f"✅ Title generation successful with {model_config['name']}")
            return result.final_output
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"⚠️ Title generation failed with {model_config['name']}: {error_msg}")
            
            # If this is not the last model, continue to next one
            if attempt < len(models_to_try) - 1:
                logger.info(f"🔄 Trying next model...")
                # Optional: Add a small delay between retries
                await asyncio.sleep(1)
                continue
            else:
                # This was the last model, raise the error
                logger.error(f"❌ All {len(models_to_try)} models failed for title generation")
                raise TitleGenerationError(f"Title generation failed with all models. Last error: {error_msg}")
    
    # This should never be reached, but just in case
    raise TitleGenerationError("Title generation failed: No models available")
