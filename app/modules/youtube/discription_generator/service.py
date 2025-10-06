from agents import Agent, Runner, set_tracing_disabled, ModelSettings, OpenAIChatCompletionsModel, AsyncOpenAI
from agents.extensions.models.litellm_model import LitellmModel
from pydantic import BaseModel, Field
from typing import Optional
from sqlmodel import Session, select
from uuid import UUID
import asyncio

from ..gemini.service import get_user_gemini_api_key
from ..video.model import Video
from .error_models import (
    DescriptionGenerationError,
    VideoNotFoundError,
    VideoTranscriptNotFoundError,
    ApiKeyMissingError,
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger
from ..helpers.transcript_dependency import get_video_transcript

set_tracing_disabled(True)
logger = get_logger("DESCRIPTION_GENERATOR_SERVICE")


class VideoSummaryGeneratorOutput(BaseModel):
    summary_of_the_video : str = Field(..., description=f"summary of the video")
    topics_as_hastages: list[str] = Field(..., description="topics as hastages")
    keywords: list[str] = Field(..., description="keywords SEO friendly for Youtube")






# Core service functions with proper error handling

async def generate_video_description(
    video_id: UUID, 
    user_id: UUID, 
    db: Session, 
    custom_template: Optional[str] = None
) -> dict:
    """
    Generate description for a video using its transcript
    """
    # Validate API key
    api_key =   get_user_gemini_api_key(user_id, db)
    if not api_key:
        raise ApiKeyMissingError("Gemini API key is required for description generation", user_id=str(user_id))
    
    # Get video transcript
    transcript = get_video_transcript(video_id, user_id, db)
    if not transcript:
        raise VideoTranscriptNotFoundError("Video transcript not found or not generated yet", video_id=str(video_id), user_id=str(user_id))
    
    # Use default template if none provided
    if not custom_template:
        custom_template = """
🔔 Subscribe for more educational content!
👍 Like this video if it helped you
💬 Comment below with your questions
📱 Follow us on social media for updates

#Education #Learning #Tutorial
"""
    
    # Generate description
    try:
        description = await _video_summary_generator_agent(transcript, custom_template, api_key)
        
        logger.info(f"Description generated successfully for video {video_id}")
        
        return {
            "video_id": video_id,
            "generated_description": description,
            "success": True,
            "message": "Description generated successfully"
        }
        
    except Exception as e:
        raise DescriptionGenerationError(f"Error generating description: {str(e)}", video_id=str(video_id), user_id=str(user_id))


async def save_video_description(
    video_id: UUID,
    user_id: UUID,
    description: str,
    db: Session
) -> dict:
    """
    Save the generated description to the video record
    """
    # Validate description
    if not description or not description.strip():
        raise ValidationError("Description cannot be empty", field="description", error_type="missing_field")
    
    if len(description.strip()) < 10:
        raise ValidationError("Description must be at least 10 characters long", field="description", error_type="too_short")
    
    if len(description.strip()) > 5000:
        raise ValidationError("Description must be less than 5000 characters", field="description", error_type="too_long")
    
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
        video.description = description.strip()
        db.add(video)
        db.commit()
        
        logger.info(f"Description saved successfully for video {video_id}")
        
        return {
            "success": True,
            "message": "Description saved successfully",
            "video_id": str(video_id),
            "description": description.strip()
        }
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error saving description: {str(e)}", operation="save_video_description", error_type="transaction")


async def regenerate_video_description(
    video_id: UUID,
    user_id: UUID,
    db: Session,
    custom_template: Optional[str] = None
) -> dict:
    """
    Regenerate description for a video
    """
    return await generate_video_description(video_id, user_id, db, custom_template)




# ======================================
# ======================================

# Helper functions


# ======================================
# ======================================


def _clean_text_for_youtube(text: str) -> str:
    """
    Clean text to make it YouTube-compatible while preserving formatting and spacing.
    """
    import re

    # Remove markdown formatting but preserve structure
    # text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # # Remove code blocks but preserve content
    # text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # Preserve spacing
    # text = re.sub(r'\n{3,}', '\n\n', text)
    # text = re.sub(r'[ \t]+', ' ', text)
    # text = re.sub(r'\n +', '\n', text)
    # text = re.sub(r' +\n', '\n', text)

    # Final cleanup (preserve #)
    # text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\n\r\t\@\&\+\=\[\]\{\}\|\~\`\'\"\<\>\/\\\#]', '', text)

    return text.strip()


def _convert_to_youtube_description(summary_output: VideoSummaryGeneratorOutput, custom_template_for_youtube_description: str, max_length: int = 4900) -> str:
    """
    Convert VideoSummaryGeneratorOutput to YouTube-compatible description format.
    """
    description_parts = []
    
    # Add keywords at the beginning for better SEO (as YouTube suggests)
    if summary_output.keywords:
        keywords = " ".join(summary_output.keywords)
        description_parts.append(keywords)
        description_parts.append("")
    
    description_parts.extend([])

    if summary_output.summary_of_the_video:
        description_parts.append("📚 VIDEO SUMMARY")
        description_parts.append("=" * 50)
        description_parts.append(summary_output.summary_of_the_video)
        description_parts.append("")

    description_parts.append(custom_template_for_youtube_description)

    # Add hashtags section
    if summary_output.topics_as_hastages:
        description_parts.append("🏷️ TAGS")
        description_parts.append("=" * 50)
        hashtags = " ".join(summary_output.topics_as_hastages)
        description_parts.append(hashtags)

    # Join description before cleaning
    full_description = "\n".join(description_parts)
    
    # Clean the main description
    final_output = _clean_text_for_youtube(full_description)

    return final_output[:max_length]


async def _video_summary_generator_agent(transcript, custom_template_for_youtube_description, api_key):
    """
    Generate a video summary and convert it to YouTube description format with retry logic
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
    input_prompt = f"""
    Analyze this YouTube video transcript and create an engaging, comprehensive description that will attract viewers and improve discoverability.

    TRANSCRIPT:
    {transcript}

    REQUIREMENTS:
    - Create a compelling 300-500 word summary that captures the video's essence
    - Generate 10-15 SEO-optimized keywords that people actually search for
    - Create 8-12 relevant hashtags mixing popular and niche tags
    - Adapt the tone to match the video content (educational, entertainment, review, etc.)
    - Highlight key value propositions and what viewers will gain
    - Use engaging language that makes people want to watch
    - Include specific details that show deep understanding of the content
    
    Make this description irresistible while staying authentic to the video's actual content and value.
    """
    
    # Try each model with retry logic
    for attempt, model_config in enumerate(models_to_try):
        try:
            logger.info(f"🔄 Attempting description generation with {model_config['name']} (attempt {attempt + 1}/{len(models_to_try)})")
            
            agent = Agent(
                name="YouTube Video Summarizer",
                model=model_config["model"],
                model_settings=ModelSettings(
                                      temperature=0.7,
                ),
                instructions="""
                You are an expert YouTube video summarizer capable of creating engaging descriptions for ANY type of video content. 
                Your job is to analyze the video transcript and create a comprehensive, attractive summary that captures the essence of the video.

                # CORE RESPONSIBILITIES:
                1. **Universal Content Analysis**: Summarize ANY video type including:
                   - Educational tutorials and courses
                   - Entertainment content (vlogs, comedy, reactions)
                   - Gaming videos and walkthroughs
                   - Product reviews and unboxings
                   - Music videos and performances
                   - News and documentary content
                   - Lifestyle and travel content
                   - Business and motivational content
                   - Sports and fitness content
                   - Cooking and DIY tutorials
                   - Technology reviews and demos
                   - And any other video category

                2. **Engaging Summary Creation**: 
                   - Write compelling summaries that hook viewers
                   - Use dynamic language that matches the video's tone and energy
                   - Highlight key moments, insights, or entertainment value
                   - Make complex topics accessible and simple topics engaging
                   - Include specific details that show you understood the content

                3. **SEO-Optimized Content**:
                   - Generate relevant keywords that people actually search for
                   - Create hashtags that are trending and discoverable
                   - Use language that improves video discoverability
                   - Include topic-specific terminology naturally

                4. **Tone Adaptation**:
                   - Match the video's energy level (high-energy for gaming, professional for business, etc.)
                   - Use appropriate language for the target audience
                   - Maintain authenticity to the creator's style
                   - Be enthusiastic for entertainment content, informative for educational content

                5. **Value Proposition**:
                   - Clearly communicate what viewers will gain from watching
                   - Highlight unique insights, entertainment value, or learning outcomes
                   - Create urgency or curiosity that encourages viewing
                   - Mention specific benefits or takeaways

                # SUMMARY GUIDELINES:
                - **Length**: Aim for 300-500 words of rich, detailed content
                - **Structure**: Organize information logically with smooth flow
                - **Language**: Use active voice, vivid descriptions, and engaging vocabulary
                - **Specificity**: Include concrete details, numbers, examples, or quotes when relevant
                - **Accessibility**: Make content understandable to the target audience
                - **Authenticity**: Reflect the genuine value and personality of the video

                # KEYWORDS & HASHTAGS:
                - **Keywords**: Generate 10-15 highly relevant, searchable terms
                - **Hashtags**: Create 8-12 discoverable hashtags mixing popular and niche tags
                - **Relevance**: Ensure all tags directly relate to the video content
                - **Variety**: Include both broad category tags and specific content tags

                Create a summary that makes viewers excited to watch the video while accurately representing its content and value.
                """,
                output_type=VideoSummaryGeneratorOutput,
            )

            result = await Runner.run(
                agent,
                input=input_prompt,
            )

            output = result.final_output
            youtube_description = _convert_to_youtube_description(output, custom_template_for_youtube_description)
            
            logger.info(f"✅ Description generation successful with {model_config['name']}")
            return youtube_description
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"⚠️ Description generation failed with {model_config['name']}: {error_msg}")
            
            # If this is not the last model, continue to next one
            if attempt < len(models_to_try) - 1:
                logger.info(f"🔄 Trying next model...")
                # Optional: Add a small delay between retries
                await asyncio.sleep(1)
                continue
            else:
                # This was the last model, raise the error
                logger.error(f"❌ All {len(models_to_try)} models failed for description generation")
                raise DescriptionGenerationError(f"Description generation failed with all models. Last error: {error_msg}")
    
    # This should never be reached, but just in case
    raise DescriptionGenerationError("Description generation failed: No models available")

