from typing import Dict, Any, Optional
import random
from urllib.parse import quote, urlencode
import asyncio
from sqlmodel import Session, select
from uuid import UUID

from ..video.model import Video
from ..thumbnail_generator.error_models import (
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


from agents import Agent, Runner, set_tracing_disabled, SQLiteSession
from dotenv import load_dotenv
from agents.extensions.models.litellm_model import LitellmModel, ModelSettings
import os
import re
from pydantic import BaseModel, Field
import asyncio
from typing import List
BASE_URL = "https://image.pollinations.ai"
logger = get_logger("THUMBNAIL_GENERATOR_SERVICE")

async def generate_video_thumbnail(
    video_id: UUID, 
    transcript: str,
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
    

    # Generate thumbnail
    try:
        result = await _agent_runner(transcript, api_key)
        
        if not result:
            raise ThumbnailGenerationError("Failed to generate thumbnail", video_id=str(video_id), user_id=str(user_id))
        
        logger.info(f"Thumbnail generated successfully for video {video_id}")
        
        return {
            "success": True,
            "message": "Thumbnail generated successfully",
            "image_url": result.get("imageUrl"),
        }
        
    except Exception as e:
        raise ThumbnailGenerationError(f"Error generating thumbnail: {str(e)}", video_id=str(video_id), user_id=str(user_id))



























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


async def _agent_runner(transcript: str,api_key: str) -> str:
    """
    Runs the agent to generate thumbnail prompts for a given transcript.
    
    Args:
        transcript: The transcript of the video to generate thumbnail prompts for
        
    Returns:
        The generated thumbnail prompts
    """

    if api_key:
        model = LitellmModel(
            model="gemini/gemini-2.0-flash",
            api_key=api_key,
        )
    else:
        model = LitellmModel(
            model="gemini/gemini-2.0-flash",
            api_key="AIzaSyBf-7p-DiTq3s1rLwwnC_jaXVWEK8naVjE",
        )

    agent = Agent(
        name="YouTube Thumbnail Prompt Generator",
        model_settings=ModelSettings(
            temperature=0.7,
            frequency_penalty=1
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

    # PROMPT EXAMPLES FOR MAXIMUM VISUAL IMPACT:
    - "ULTRA-CINEMATIC 3D render of a futuristic holographic code editor with EXPLOSIVE neon blue and electric purple color scheme featuring gradient transitions from deep cobalt to vibrant cyan, floating 3D code blocks with intricate particle effects and energy trails, dark glass background with animated circuit patterns and flowing data streams, dramatic backlighting creating golden rim effects with volumetric light rays, multiple floating screens with holographic UI elements displaying real-time code execution, high-tech workspace with floating geometric shapes including cubes, spheres, and pyramids, programming symbols and brackets floating in space with subtle glow effects, simple 'PYTHON' text in glowing neon with 3D depth and shadow casting, maximum visual impact composition with rule of thirds framing, depth of field focusing on main elements, premium materials including brushed aluminum, tempered glass, and holographic surfaces, atmospheric fog and light particles creating depth, cinematic color grading with high contrast and saturation"
    - "CINEMATIC SPLIT-SCREEN with EXPLOSIVE visual contrast: left side showing basic programming in monochrome with grainy texture and low contrast, right side displaying ADVANCED OOPS with interconnected neon nodes and electric blue data streams flowing in complex patterns, DRAMATIC lighting with orange and cyan color grading creating dramatic shadows and highlights, floating 3D geometric shapes representing classes and objects with metallic surfaces and neon edges, modern gradient background with particle effects and energy fields, professional coding environment with visual programming icons and flowcharts rendered in high detail, minimal 'OOP' text overlay with subtle glow, maximum visual appeal with dynamic composition, detailed material specifications including chrome, neon tubing, and holographic displays, atmospheric effects with smoke and light rays, depth of field with selective focus, geometric arrangements following golden ratio principles"
    - "PHOTOREALISTIC PREMIUM tech workspace with ultra-modern laptop displaying Python IDE with crystal-clear screen resolution, multiple floating holographic screens showing OOPS concepts with detailed UI elements and code syntax highlighting, WARM GOLDEN HOUR lighting creating dramatic shadows with soft rim lighting, premium coffee cup and tech accessories with realistic materials and reflections, depth of field effect focusing on main screen with bokeh background, high-quality materials and textures including brushed steel, tempered glass, and premium plastics, professional development environment with code symbols and programming diagrams rendered in high detail, simple 'CODE' text in modern typography with subtle 3D effects, maximum visual impact with cinematic composition, detailed surface textures including matte finishes and glossy reflections, atmospheric lighting with volumetric effects, geometric arrangements with precise positioning and spacing"

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
        model=model,
        output_type=ThumbnailPromptOutput,
    )
    input = "Generate 1 EXTREMELY detailed and VISUALLY STUNNING thumbnail prompt that would create a VIRAL-QUALITY YouTube thumbnail with maximum click-through rates. The prompt MUST be 150-250 words with ULTRA-DETAILED descriptions of every visual element, including specific materials, lighting, colors, textures, and atmospheric effects. IMPORTANT: Use minimal, simple text only when needed (like 'PYTHON', 'CODE', 'OOP') and focus primarily on visual elements, symbols, and icons to avoid AI spelling mistakes. for the video: " + transcript
    result =  await Runner.run(agent, input)
    print("Generated thumbnail prompt:")
    print(result)

    prompt = result.final_output.thumbnail_prompt
    image_url = await _generate_image_url(prompt.prompt)
    

    return image_url

