from typing import Dict, Any, Optional
import random
from urllib.parse import quote, urlencode
import asyncio
from sqlmodel import Session, select
from uuid import UUID
from ..helpers.download_image_from_url import download_image_from_url
from ..video.model import Video
from .error_models import (
    ThumbnailGenerationError,
    ThumbnailSaveError,
    ThumbnailUploadError,
    VideoNotFoundError,
    VideoTranscriptNotFoundError,
    ApiKeyMissingError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger
from ..helpers.transcript_dependency import get_video_transcript
from ..gemini.service import get_user_gemini_api_key


from agents import Agent, Runner, set_tracing_disabled, SQLiteSession, OpenAIChatCompletionsModel, AsyncOpenAI
from dotenv import load_dotenv
from agents.extensions.models.litellm_model import LitellmModel, ModelSettings
import os
import re
from pydantic import BaseModel, Field
import asyncio
from typing import List
BASE_URL = "https://image.pollinations.ai"
logger = get_logger("THUMBNAIL_GENERATOR_SERVICE")



# Core service functions with proper error handling

async def generate_video_thumbnail(
    video_id: UUID, 
    user_id: UUID, 
    db: Session
) -> dict:
    """
    Generate thumbnail image URL for a video using its transcript
    """
    # Validate API key
    api_key = get_user_gemini_api_key(user_id, db)
    if not api_key:
        raise ApiKeyMissingError("Gemini API key is required for thumbnail generation", user_id=str(user_id))
    
    # Get video transcript
    transcript = get_video_transcript(video_id, user_id, db)
    if not transcript:
        raise VideoTranscriptNotFoundError("Video transcript not found or not generated yet", video_id=str(video_id), user_id=str(user_id))
    
    # Generate thumbnail
    try:
        result = await _agent_runner(transcript, api_key)
        
        if not result:
            raise ThumbnailGenerationError("Failed to generate thumbnail", video_id=str(video_id), user_id=str(user_id))
        
        logger.info(f"Thumbnail generated successfully for video {video_id}")
        
        return {
            "success": True,
            "message": "Thumbnail generated successfully",
            "video_id": str(video_id),
            "image_url": result.get("imageUrl"),
            "width": result.get("width"),
            "height": result.get("height"),
            "prompt": result.get("prompt"),
            "model": result.get("model"),
            "seed": result.get("seed")
        }
        
    except Exception as e:
        raise ThumbnailGenerationError(f"Error generating thumbnail: {str(e)}", video_id=str(video_id), user_id=str(user_id))


async def save_video_thumbnail(
    video_id: UUID,
    user_id: UUID,
    thumbnail_url: str,
    db: Session
) -> dict:
    """
    Save the thumbnail URL to the video record
    """
    # Validate thumbnail URL
    if not thumbnail_url or not thumbnail_url.strip():
        raise ValidationError("Thumbnail URL cannot be empty", field="thumbnail_url", error_type="missing_field")
    
    if len(thumbnail_url.strip()) < 10:
        raise ValidationError("Thumbnail URL must be at least 10 characters long", field="thumbnail_url", error_type="too_short")
    
    if not thumbnail_url.strip().startswith(('http://', 'https://')):
        raise ValidationError("Thumbnail URL must be a valid HTTP/HTTPS URL", field="thumbnail_url", error_type="invalid_url")
    # download thumnail from url
    thumbnail_path = await download_image_from_url(url=thumbnail_url,dir_path="thumbnails",video_id=video_id)

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
        video.thumbnail_url = thumbnail_url.strip()
        video.thumbnail_path=thumbnail_path["custom_thumbnail_path"]
        db.add(video)
        db.commit()
        
        logger.info(f"Thumbnail saved successfully for video {video_id}")
        
        return {
            "success": True,
            "message": "Thumbnail saved successfully",
            "video_id": str(video_id),
            "thumbnail_url": thumbnail_url.strip(),
            "thumbnail_path": thumbnail_path["custom_thumbnail_path"]
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error saving thumbnail: {str(e)}", operation="save_video_thumbnail", error_type="transaction")


async def upload_custom_thumbnail(
    video_id: UUID,
    user_id: UUID,
    file_content: bytes,
    filename: str,
    db: Session
) -> dict:
    """
    Upload and save a custom thumbnail file
    """
    # Validate file
    if not file_content:
        raise ValidationError("File content cannot be empty", field="file", error_type="missing_file")
    
    if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
        raise ValidationError("File size must be less than 10MB", field="file", error_type="file_too_large")
    
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError("File must be an image (jpg, jpeg, png, gif, webp)", field="file", error_type="invalid_file_type")
    
    # Check if video exists
    statement = select(Video).where(
        Video.id == video_id,
        Video.user_id == user_id
    )
    video = db.exec(statement).first()
    
    if not video:
        raise VideoNotFoundError("Video not found", video_id=str(video_id), user_id=str(user_id))
    
    # Save file and update database
    try:
        import os
        from pathlib import Path
        
        # Create thumbnails directory if it doesn't exist
        thumbnails_dir = Path("thumbnails")
        thumbnails_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        import uuid
        unique_filename = f"{video_id}_{uuid.uuid4()}{Path(filename).suffix}"
        filepath = thumbnails_dir / unique_filename
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        # Update video record
        video.thumbnail_url = str(filepath)
        db.add(video)
        db.commit()
        
        logger.info(f"Custom thumbnail uploaded successfully for video {video_id}")
        
        return {
            "success": True,
            "message": "Custom thumbnail uploaded successfully",
            "video_id": str(video_id),
            "thumbnail_url": str(filepath),
            "filename": unique_filename
        }
        
    except Exception as e:
        db.rollback()
        # Clean up file if it was created
        if 'filepath' in locals() and filepath.exists():
            filepath.unlink()
        raise DatabaseError(f"Error uploading thumbnail: {str(e)}", operation="upload_custom_thumbnail", error_type="transaction")






# ======================================
# ======================================

# Helper functions


# ======================================
# ======================================


def _rand_seed() -> int:
    return random.randint(0, 100000000)


async def _generate_image_url(
    prompt: str,
    model: str = "nanobanana",
    seed: Optional[int] = None,
    width: int = 1280,
    height: int = 720,
    enhance: bool = True,
    safe: bool = False,
) -> Dict[str, Any]:
    """
    Generates an image URL from a text prompt using the Pollinations Image API.
    Always includes nologo=true and private=true.

    Returns a dict containing the URL and metadata.
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Prompt is required and must be a string")

    if seed is None:
        seed = _rand_seed()

    query = {
        "model": model,
        "seed": seed,
        "width": width,
        "height": height,
        "nologo": "true",
        "private": "true",
        "safe": str(safe).lower(),
        "token":"L3g92SSpMD_I6mnr"  # "true"/"false"
    }
    if enhance:
        query["enhance"] = "true"

    encoded_prompt = quote(prompt, safe="")
    url = f"{BASE_URL}/prompt/{encoded_prompt}?{urlencode(query)}"
    print(url)
    return {
        "imageUrl": url,
        "prompt": prompt,
        "width": width,
        "height": height,
        "model": model,
        "seed": seed,
        "enhance": enhance,
        "private": True,
        "nologo": True,
        "safe": safe,
    }


async def _download_image(url: str, filename: str) -> str:
    """
    Downloads an image from a URL and saves it to the images directory.
    
    Args:
        url: The URL of the image to download
        filename: The filename to save the image as
        
    Returns:
        The full path to the saved image file
    """
    import os
    import aiohttp
    from pathlib import Path

    # Create images directory if it doesn't exist
    image_dir = Path("images")
    image_dir.mkdir(exist_ok=True)
    
    # Add .png extension if not present
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename += '.png'
        
    filepath = image_dir / filename
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        f.write(await response.read())
                    return str(filepath)
                else:
                    raise Exception(f"Failed to download image. Status code: {response.status}")
                    
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None





set_tracing_disabled(True)
load_dotenv()


class ThumbnailPrompt(BaseModel):
    prompt: str = Field(..., description="A high-quality YouTube thumbnail generation prompt")

class ThumbnailPromptOutput(BaseModel):
    thumbnail_prompt: ThumbnailPrompt = Field(..., description="One high-quality YouTube thumbnail generation prompt")


async def _agent_runner(transcript: str, api_key: str) -> str:
    """
    Runs the agent to generate thumbnail prompts for a given transcript with retry logic
    
    Args:
        transcript: The transcript of the video to generate thumbnail prompts for
        api_key: API key for Gemini (if available)
        
    Returns:
        The generated thumbnail prompts and image URL
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
    input_prompt = "Generate 1 EXTREMELY detailed and VISUALLY STUNNING thumbnail prompt that would create a VIRAL-QUALITY YouTube thumbnail with maximum click-through rates. The prompt MUST be 150-250 words with ULTRA-DETAILED descriptions of every visual element, including specific materials, lighting, colors, textures, and atmospheric effects. IMPORTANT: Use minimal, simple text only when needed (like 'PYTHON', 'CODE', 'OOP') and focus primarily on visual elements, symbols, and icons to avoid AI spelling mistakes. for the video: " + transcript
    
    # Try each model with retry logic
    for attempt, model_config in enumerate(models_to_try):
        try:
            logger.info(f"🔄 Attempting thumbnail generation with {model_config['name']} (attempt {attempt + 1}/{len(models_to_try)})")
            
            agent = Agent(
                name="YouTube Thumbnail Prompt Generator",
                model=model_config["model"],
                model_settings=ModelSettings(
                    temperature=0.7,
                ),
                instructions="""You are a YouTube thumbnail prompt generator. You are given a transcript of a YouTube video and you need to generate 5 EXTREMELY VISUALLY APPEALING and EYE-CATCHING prompts for creating YouTube thumbnails.

        # CRITICAL REQUIREMENTS FOR MAXIMUM VISUAL IMPACT:
        1. Generate exactly 1 thumbnail prompt
        2. The prompt should be 150-250 words with EXTREMELY detailed descriptions
        3. Focus on the main topics and concepts taught in the video
        4. Make the prompt ABSOLUTELY STUNNING and impossible to ignore
        5. Use the MOST VISUALLY APPEALING elements possible
        6. Consider the educational nature of programming/tech videos
        7. Use EXTREMELY vivid, descriptive language with maximum visual impact
        8. Include multiple layers of visual elements in the prompt
        9. Provide ULTRA-DETAILED descriptions for every visual element

        # ULTRA-DETAILED PROMPT STRUCTURE (150-250 words):
        The prompt MUST include:
        - Main subject/focus (code, concepts, tools) with maximum visual appeal and detailed description
        - Specific visual style (3D, photorealistic, cinematic, ultra-modern) with detailed rendering specifications
        - EXPLOSIVE color palette with high contrast and saturation, including specific color combinations and gradients
        - Dramatic lighting and atmospheric effects with detailed light positioning and intensity
        - Background and environment with maximum visual impact, including detailed textures and materials
        - High-tech elements (screens, devices, interfaces, holograms, code symbols) with detailed specifications
        - Visual programming icons and symbols (brackets, arrows, flowcharts, diagrams) with detailed positioning
        - Mood and atmosphere that's impossible to ignore, with detailed emotional and visual tone
        - Composition that follows viral thumbnail principles with detailed camera angles and framing
        - MINIMAL TEXT ONLY when absolutely necessary (simple words like "CODE", "PYTHON", "OOP" - keep it very basic)
        - Detailed material specifications (glass, metal, neon, holographic, matte, glossy, etc.)
        - Specific particle effects and atmospheric details (smoke, dust, light rays, energy fields)
        - Detailed depth of field and focus specifications
        - Specific geometric shapes and their detailed arrangements
        - Detailed surface textures and reflections
        - Specific animation or motion suggestions
        - Detailed shadow and highlight specifications

        # VISUAL ELEMENTS FOR MAXIMUM IMPACT:
        - EXPLOSIVE color schemes (neon, electric, rainbow, high contrast)
        - DRAMATIC lighting (backlit, rim lighting, golden hour, dramatic shadows)
        - STUNNING backgrounds (gradient, abstract, space, futuristic)
        - VIRAL composition techniques (rule of thirds, asymmetry, dramatic angles)
        - DEPTH and perspective with maximum visual impact
        - PREMIUM materials and textures (glass, metal, neon, holographic)
        - ATMOSPHERIC effects (particles, glow, light trails, explosions)
        - VISUAL SYMBOLS and ICONS as primary elements (code symbols, programming icons, tech elements)
        - MINIMAL TEXT when needed (simple, short words only)

        # AVOID:
        - Generic or basic descriptions
        - Prompts under 150 words
        - Vague visual descriptions
        - Prompts that don't relate to the video content
        - Simple one-sentence descriptions
        - Boring or unappealing visual elements
        - COMPLEX TEXT OVERLAYS or long sentences (AI will misspell them)
        - Text-based elements that require complex spelling accuracy
        - Long phrases or multiple words in text
        - Short, incomplete descriptions
        - Lack of detail in visual elements

        Generate 1 EXTREMELY detailed and VISUALLY STUNNING thumbnail prompt that would create a VIRAL-QUALITY YouTube thumbnail with maximum click-through rates. The prompt MUST be 150-250 words with ULTRA-DETAILED descriptions of every visual element, including specific materials, lighting, colors, textures, and atmospheric effects. IMPORTANT: Use minimal, simple text only when needed (like "PYTHON", "CODE", "OOP") and focus primarily on visual elements, symbols, and icons to avoid AI spelling mistakes.
        """,
                output_type=ThumbnailPromptOutput,
            )
            
            result = await Runner.run(agent, input_prompt)
            print("Generated thumbnail prompt:")
            print(result)

            prompt = result.final_output.thumbnail_prompt
            image_url = await _generate_image_url(prompt.prompt)
            
            logger.info(f"✅ Thumbnail generation successful with {model_config['name']}")
            return image_url
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"⚠️ Thumbnail generation failed with {model_config['name']}: {error_msg}")
            
            # If this is not the last model, continue to next one
            if attempt < len(models_to_try) - 1:
                logger.info(f"🔄 Trying next model...")
                # Optional: Add a small delay between retries
                await asyncio.sleep(1)
                continue
            else:
                # This was the last model, raise the error
                logger.error(f"❌ All {len(models_to_try)} models failed for thumbnail generation")
                raise ThumbnailGenerationError(f"Thumbnail generation failed with all models. Last error: {error_msg}")
    
    # This should never be reached, but just in case
    raise ThumbnailGenerationError("Thumbnail generation failed: No models available")

