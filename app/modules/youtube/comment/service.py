"""
Service layer for video comments
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlmodel import Session, select
from uuid import UUID

from .model import VideoComment, CommentResponse, CommentsListResponse, DeleteCommentResponse, ReplyCommentRequest, ReplyMultipleCommentsRequest, ReplyCommentResponse, ReplyCommentsResponse, ReplyGenerationRequest, ReplyGenerationResponse, GeneratedReply
from ..helpers.youtube_client import get_youtube_client
from ....utils.my_logger import get_logger
from ..helpers.transcript_dependency import get_video_transcript
from ..gemini.service import get_user_gemini_api_key

# AI Agent imports
from agents import Agent, Runner, set_tracing_disabled, ModelSettings, OpenAIChatCompletionsModel, AsyncOpenAI
from agents.extensions.models.litellm_model import LitellmModel
from pydantic import BaseModel, Field
import asyncio
from dotenv import load_dotenv

load_dotenv()
set_tracing_disabled(True)

logger = get_logger("VIDEO_COMMENTS_SERVICE")


class AgentReplyOutput(BaseModel):
    """Single reply output from AI agent"""
    reply_text: str = Field(..., description="Generated reply text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence score")


class ReplyGeneratorOutput(BaseModel):
    """Output model for AI reply generator"""
    replies: List[AgentReplyOutput] = Field(..., description="List of generated replies")


def get_video_comments_service(
    video_id: str, 
    user_id: UUID, 
    db: Session, 
    limit: int = 20, 
    refresh: bool = False,
    include_replies: bool = True
) -> Dict[str, Any]:
    """Get comments for a video from database or YouTube API"""
    try:
        # Check if comments exist in database for this user and video
        statement = select(VideoComment).where(
            VideoComment.video_id == video_id,
            VideoComment.user_id == user_id
        ).order_by(VideoComment.published_at.desc()).limit(limit)
        
        existing_comments = db.exec(statement).all()
        
        # Determine if we need to fetch from YouTube
        should_fetch_from_youtube = refresh or not existing_comments
        
        if should_fetch_from_youtube:
            # Fetch from YouTube API
            youtube_comments = _fetch_comments_from_youtube_api(
                video_id, user_id, db, limit, include_replies
            )
            
            if "error" in youtube_comments:
                return {
                    "success": False,
                    "message": youtube_comments["error"],
                    "data": None
                }
            
            # Save to database
            saved_comments = _save_comments_to_database(
                video_id, youtube_comments, user_id, db
            )
            comments = saved_comments
            message = "Comments refreshed from YouTube successfully" if refresh else "Comments fetched from YouTube and saved to database"
            comments_source = "youtube"
            logger.info(f"Successfully {'refreshed' if refresh else 'fetched'} comments for video_id {video_id}")
        else:
            comments = existing_comments
            message = "Comments retrieved from database successfully"
            comments_source = "database"
            logger.info(f"Successfully retrieved comments from database for video_id {video_id}")
        
        # Convert to response format
        comment_responses = []
        for comment in comments:
            comment_response = CommentResponse(
                comment_id=comment.comment_id,
                parent_comment_id=comment.parent_comment_id,
                author_display_name=comment.author_display_name,
                author_channel_id=comment.author_channel_id,
                author_profile_image_url=comment.author_profile_image_url,
                text_display=comment.text_display,
                text_original=comment.text_original,
                like_count=comment.like_count,
                published_at=comment.published_at,
                updated_at=comment.updated_at,
                is_reply=comment.is_reply,
                reply_count=comment.reply_count
            )
            comment_responses.append(comment_response)
        
        # Create response
        response_data = CommentsListResponse(
            video_id=video_id,
            total_comments=len(comment_responses),
            comments=comment_responses,
            limit=limit,
            refresh=refresh,
            comments_source=comments_source
        )
        
        return {
            "success": True,
            "message": message,
            "data": response_data
        }
        
    except Exception as e:
        logger.error(f"Error retrieving comments: {str(e)}")
        return {
            "success": False,
            "message": f"Error retrieving comments: {str(e)}",
            "data": None
        }


def delete_comment_service(
    comment_id: str, 
    user_id: UUID, 
    db: Session
) -> Dict[str, Any]:
    """Delete a comment from YouTube and remove from database"""
    try:
        # Check if comment exists in our database (for user verification)
        statement = select(VideoComment).where(
            VideoComment.comment_id == comment_id,
            VideoComment.user_id == user_id
        )
        comment_record = db.exec(statement).first()
        
        if not comment_record:
            return {
                "success": False,
                "message": "Comment not found in database for the current user",
                "deleted_comment_id": None
            }
        
        # Get YouTube client
        youtube_client = get_youtube_client(user_id, db)
        if not youtube_client:
            return {
                "success": False,
                "message": "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens.",
                "deleted_comment_id": None
            }
        
        # Verify comment exists on YouTube and user owns it
        try:
            # Check if comment exists and user has access to it
            comment_check = youtube_client.comments().list(
                part='snippet',
                id=comment_id
            ).execute()
            
            if not comment_check.get('items'):
                return {
                    "success": False,
                    "message": "Comment not found on YouTube or you don't have permission to delete it",
                    "deleted_comment_id": None
                }
            
        except Exception as e:
            logger.error(f"Error checking comment ownership: {str(e)}")
            return {
                "success": False,
                "message": f"Error verifying comment ownership: {str(e)}",
                "deleted_comment_id": None
            }
        
        # Delete comment from YouTube
        try:
            youtube_client.comments().delete(id=comment_id).execute()
            logger.info(f"Successfully deleted comment {comment_id} from YouTube")
            
        except Exception as e:
            logger.error(f"Error deleting comment from YouTube: {str(e)}")
            return {
                "success": False,
                "message": f"Error deleting comment from YouTube: {str(e)}",
                "deleted_comment_id": None
            }
        
        # Remove comment from our database
        try:
            db.delete(comment_record)
            db.commit()
            logger.info(f"Successfully removed comment {comment_id} from database")
            
        except Exception as e:
            logger.error(f"Error removing comment from database: {str(e)}")
            # Don't fail the operation if database cleanup fails
            logger.warning("Comment deleted from YouTube but database cleanup failed")
        
        return {
            "success": True,
            "message": "Comment deleted successfully from YouTube and removed from database",
            "deleted_comment_id": comment_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting comment: {str(e)}")
        return {
            "success": False,
            "message": f"Error deleting comment: {str(e)}",
            "deleted_comment_id": None
        }


def reply_to_comment_service(
    parent_comment_id: str,
    reply_text: str,
    user_id: UUID,
    db: Session
) -> Dict[str, Any]:
    """Reply to a single comment on YouTube and save to database"""
    try:
        # Get YouTube client
        youtube_client = get_youtube_client(user_id, db)
        if not youtube_client:
            return {
                "success": False,
                "message": "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens.",
                "parent_comment_id": parent_comment_id,
                "reply_comment_id": None,
                "reply_text": reply_text
            }
        
        # Try to get video_id from database first (more reliable)
        video_id = None
        try:
            statement = select(VideoComment).where(
                VideoComment.comment_id == parent_comment_id,
                VideoComment.user_id == user_id
            )
            db_comment = db.exec(statement).first()
            if db_comment:
                video_id = db_comment.video_id
                logger.info(f"Found video_id {video_id} from database for comment {parent_comment_id}")
        except Exception as db_error:
            logger.warning(f"Could not find video_id in database: {str(db_error)}")
        
        # If not in database, try to verify parent comment exists and get video_id
        if not video_id:
            try:
                parent_comment_check = youtube_client.comments().list(
                    part='snippet',
                    id=parent_comment_id
                ).execute()
                
                if not parent_comment_check.get('items'):
                    return {
                        "success": False,
                        "message": "Parent comment not found on YouTube",
                        "parent_comment_id": parent_comment_id,
                        "reply_comment_id": None,
                        "reply_text": reply_text
                    }
                
                # Try to get video_id from the comment snippet
                parent_comment_snippet = parent_comment_check['items'][0]['snippet']
                video_id = parent_comment_snippet.get('videoId')
                
                if not video_id:
                    logger.warning(f"videoId not available in comment snippet")
                    video_id = "unknown"
                
            except Exception as e:
                logger.error(f"Error checking parent comment: {str(e)}")
                return {
                    "success": False,
                    "message": f"Error verifying parent comment: {str(e)}",
                    "parent_comment_id": parent_comment_id,
                    "reply_comment_id": None,
                    "reply_text": reply_text
                }
        
        # Post reply to YouTube (requires videoId in the request body)
        try:
            if not video_id or video_id == "unknown":
                return {
                    "success": False,
                    "message": "Cannot post reply: video ID is required but not available",
                    "parent_comment_id": parent_comment_id,
                    "reply_comment_id": None,
                    "reply_text": reply_text
                }
            
            # Post reply to YouTube
            reply_response = youtube_client.comments().insert(
                part='snippet',
                body={
                    'snippet': {
                        'parentId': parent_comment_id,
                        'videoId': video_id,
                        'textOriginal': reply_text
                    }
                }
            ).execute()
            
            reply_comment_id = reply_response['id']
            logger.info(f"Successfully posted reply {reply_comment_id} to comment {parent_comment_id}")
            
        except Exception as e:
            logger.error(f"Error posting reply to YouTube: {str(e)}")
            
            # Check if this is a reply to a reply (YouTube API limitation)
            if "processingFailure" in str(e) and "." in parent_comment_id:
                return {
                    "success": False,
                    "message": "YouTube API does not support replying to replies. You can only reply to top-level comments. Please use the original comment ID instead.",
                    "parent_comment_id": parent_comment_id,
                    "reply_comment_id": None,
                    "reply_text": reply_text
                }
            
            return {
                "success": False,
                "message": f"Error posting reply to YouTube: {str(e)}",
                "parent_comment_id": parent_comment_id,
                "reply_comment_id": None,
                "reply_text": reply_text
            }
        
        # Save reply to database
        try:
            # Get reply details from YouTube to save to database
            reply_details = youtube_client.comments().list(
                part='snippet',
                id=reply_comment_id
            ).execute()
            
            if reply_details.get('items'):
                reply_snippet = reply_details['items'][0]['snippet']
                
                # Create reply data with the video_id we used for posting
                new_reply = VideoComment(
                    video_id=video_id,  # Use the video_id we successfully used for posting
                    user_id=user_id,
                    comment_id=reply_comment_id,
                    parent_comment_id=parent_comment_id,
                    author_display_name=reply_snippet.get('authorDisplayName'),
                    author_channel_id=reply_snippet.get('authorChannelId', {}).get('value'),
                    author_profile_image_url=reply_snippet.get('authorProfileImageUrl'),
                    text_display=reply_snippet.get('textDisplay'),
                    text_original=reply_snippet.get('textOriginal'),
                    like_count=reply_snippet.get('likeCount', 0),
                    published_at=datetime.fromisoformat(reply_snippet['publishedAt'].replace('Z', '+00:00')) if reply_snippet.get('publishedAt') else None,
                    updated_at=datetime.fromisoformat(reply_snippet['updatedAt'].replace('Z', '+00:00')) if reply_snippet.get('updatedAt') else None,
                    is_reply=True,  # This is always a reply
                    reply_count=0
                )
                
                db.add(new_reply)
                db.commit()
                logger.info(f"Successfully saved reply {reply_comment_id} to database")
            
        except Exception as e:
            logger.error(f"Error saving reply to database: {str(e)}")
            # Don't fail the operation if database save fails
            logger.warning("Reply posted to YouTube but database save failed")
        
        return {
            "success": True,
            "message": "Reply posted successfully to YouTube and saved to database",
            "parent_comment_id": parent_comment_id,
            "reply_comment_id": reply_comment_id,
            "reply_text": reply_text
        }
        
    except Exception as e:
        logger.error(f"Error replying to comment: {str(e)}")
        return {
            "success": False,
            "message": f"Error replying to comment: {str(e)}",
            "parent_comment_id": parent_comment_id,
            "reply_comment_id": None,
            "reply_text": reply_text
        }


async def generate_ai_replies_service(
    comments: List[dict],
    user_id: UUID,
    db: Session
) -> ReplyGenerationResponse:
    """
    Generate AI replies for comments
    """
    try:
        # Validate input
        if not comments:
            return ReplyGenerationResponse(
                success=False,
                message="comments must be provided",
                generated_replies=[],
                total_generated=0
            )
        
        # Prepare comments data
        comments_data = []
        for comment in comments:
            comments_data.append({
                "comment_id": comment["comment_id"],
                "comment_text": comment["comment_text"],
                "author_name": "Anonymous"
            })
        
        # Generate replies using AI agent
        generated_replies = await _generate_replies_with_agent(
            comments_data, 
            user_id, 
            db
        )
        
        return ReplyGenerationResponse(
            success=True,
            message=f"Generated {len(generated_replies)} AI replies successfully",
            generated_replies=generated_replies,
            total_generated=len(generated_replies)
        )
        
    except Exception as e:
        logger.error(f"Error generating AI replies: {str(e)}")
        return ReplyGenerationResponse(
            success=False,
            message=f"Error generating AI replies: {str(e)}",
            generated_replies=[],
            total_generated=0
        )


async def _generate_replies_with_agent(
    comments_data: List[dict],
    user_id: UUID,
    db: Session
) -> List[GeneratedReply]:
    """
    Generate replies using AI agent with multiple model fallbacks
    """
    
    # Get API key for Gemini (optional)
    api_key = get_user_gemini_api_key(user_id, db)
    
    # Define models to try in order
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
    
    # Prepare the input prompt
    comments_text = "\n".join([
        f"Comment: {comment['comment_text']}"
        for comment in comments_data
    ])
    
    input_prompt = f"""
    You are a YouTube content creator's assistant helping to generate thoughtful, engaging replies to video comments.
    
    COMMENTS TO REPLY TO:
    {comments_text}
    
    REQUIREMENTS:
    - Generate one thoughtful reply for each comment above
    - Use a friendly, warm, and conversational tone
    - Maximum length per reply: 300 characters
    - Be authentic, helpful, and engaging
    - Address the commenter's specific points or questions
    - Encourage further engagement (likes, subscriptions, comments)
    - Use appropriate tone for educational content
    - Avoid generic responses - make each reply unique and specific
    - Include relevant emojis sparingly to add personality
    - Be respectful and positive even if disagreeing with the comment
    
    Generate engaging, personalized replies that will encourage viewer engagement and build community.
    """
    
    # Try each model with retry logic
    for attempt, model_config in enumerate(models_to_try):
        try:
            logger.info(f"🔄 Attempting reply generation with {model_config['name']} (attempt {attempt + 1}/{len(models_to_try)})")
            
            agent = Agent(
                name="YouTube Comment Reply Generator",
                model=model_config["model"],
                model_settings=ModelSettings(
                    temperature=0.7,
                ),
                instructions="""
                You are an expert YouTube community manager and content creator assistant specializing in generating engaging, authentic replies to video comments. Your role is to help creators build meaningful connections with their audience through thoughtful, personalized responses.

                # CORE RESPONSIBILITIES:
                1. **Authentic Engagement**: Create replies that feel genuine and personal, not robotic or template-based
                2. **Context Awareness**: Use video transcript information to provide relevant, informed responses
                3. **Community Building**: Foster positive interactions and encourage further engagement
                4. **Value Addition**: Provide helpful insights, answer questions, or add educational value
                5. **Brand Voice**: Maintain consistency with the creator's style and tone

                # REPLY GENERATION GUIDELINES:
                - **Personalization**: Address specific points mentioned in each comment
                - **Relevance**: Reference video content when it adds value to the conversation
                - **Encouragement**: Motivate viewers to engage further (like, subscribe, comment)
                - **Helpfulness**: Answer questions or provide additional insights when appropriate
                - **Positivity**: Maintain an optimistic, supportive tone even when disagreeing
                - **Authenticity**: Write as if the creator themselves wrote the reply
                - **Engagement**: End with questions or calls-to-action when natural

                # TONE ADAPTATION:
                - **Friendly**: Warm, approachable, conversational
                - **Professional**: Respectful, informative, business-appropriate
                - **Casual**: Relaxed, fun, informal with appropriate emojis
                - **Helpful**: Educational, solution-focused, value-driven

                # FORMAT REQUIREMENTS:
                - One reply per comment provided
                - Stay within specified character limits
                - Use appropriate emojis sparingly
                - Include relevant hashtags occasionally
                - Maintain natural, human-like language

                Create replies that make viewers feel heard, valued, and excited to continue engaging with the channel.
                """,
                output_type=ReplyGeneratorOutput,
            )
            
            result = await Runner.run(
                agent,
                input=input_prompt,
            )
            
            # Process the output to match our expected format
            generated_replies = []
            agent_replies = result.final_output.replies
            
            for i, reply_data in enumerate(agent_replies):
                if i < len(comments_data):
                    generated_replies.append(GeneratedReply(
                        comment_id=comments_data[i]["comment_id"],
                        comment_text=comments_data[i]["comment_text"],
                        author_name=comments_data[i]["author_name"],
                        generated_reply=reply_data.reply_text,
                        confidence=reply_data.confidence
                    ))
            
            logger.info(f"✅ Reply generation successful with {model_config['name']}")
            return generated_replies
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"⚠️ Reply generation failed with {model_config['name']}: {error_msg}")
            
            # If this is not the last model, continue to next one
            if attempt < len(models_to_try) - 1:
                logger.info(f"🔄 Trying next model...")
                await asyncio.sleep(1)
                continue
            else:
                # This was the last model, raise the error
                logger.error(f"❌ All {len(models_to_try)} models failed for reply generation")
                raise Exception(f"Reply generation failed with all models. Last error: {error_msg}")
    
    # This should never be reached, but just in case
    raise Exception("Reply generation failed: No models available")


def reply_to_multiple_comments_service(
    replies: List[ReplyCommentRequest],
    user_id: UUID,
    db: Session
) -> Dict[str, Any]:
    """Reply to multiple comments on YouTube and save to database"""
    try:
        reply_responses = []
        successful_replies = 0
        failed_replies = 0
        
        for reply_request in replies:
            try:
                # Process each reply individually
                result = reply_to_comment_service(
                    reply_request.parent_comment_id,
                    reply_request.reply_text,
                    user_id,
                    db
                )
                
                reply_response = ReplyCommentResponse(
                    parent_comment_id=reply_request.parent_comment_id,
                    reply_comment_id=result.get("reply_comment_id"),
                    reply_text=reply_request.reply_text,
                    success=result["success"],
                    message=result["message"]
                )
                
                reply_responses.append(reply_response)
                
                if result["success"]:
                    successful_replies += 1
                else:
                    failed_replies += 1
                    
            except Exception as e:
                logger.error(f"Error processing reply to {reply_request.parent_comment_id}: {str(e)}")
                reply_response = ReplyCommentResponse(
                    parent_comment_id=reply_request.parent_comment_id,
                    reply_comment_id=None,
                    reply_text=reply_request.reply_text,
                    success=False,
                    message=f"Error processing reply: {str(e)}"
                )
                
                reply_responses.append(reply_response)
                failed_replies += 1
        
        # Determine overall success
        overall_success = failed_replies == 0
        
        if overall_success:
            message = f"All {successful_replies} replies posted successfully"
        elif successful_replies > 0:
            message = f"{successful_replies} replies successful, {failed_replies} failed"
        else:
            message = f"All {failed_replies} replies failed"
        
        return {
            "success": overall_success,
            "message": message,
            "total_replies_attempted": len(replies),
            "successful_replies": successful_replies,
            "failed_replies": failed_replies,
            "replies": reply_responses
        }
        
    except Exception as e:
        logger.error(f"Error replying to multiple comments: {str(e)}")
        return {
            "success": False,
            "message": f"Error replying to multiple comments: {str(e)}",
            "total_replies_attempted": len(replies),
            "successful_replies": 0,
            "failed_replies": len(replies),
            "replies": []
        }















# ------------------------------------------------------------------------------------------------



def _fetch_comments_from_youtube_api(
    video_id: str, 
    user_id: UUID, 
    db: Session, 
    limit: int = 20,
    include_replies: bool = True
) -> Dict[str, Any]:
    """Helper function to fetch comments from YouTube API"""
    logger.info(f"Attempting to get YouTube client for user_id: {user_id}")
    youtube_client = get_youtube_client(user_id, db)
    if not youtube_client:
        logger.error(f"Failed to get YouTube client for user_id: {user_id}")
        return {"error": "Failed to authenticate with YouTube API. Please ensure you have set up YouTube credentials and OAuth tokens."}
    
    try:
        # Fetch comment threads (top-level comments)
        comments_data = []
        
        # Calculate how many top-level comments to fetch
        # If we want replies, we need fewer top-level comments to stay within limit
        top_level_limit = limit // 2 if include_replies else limit
        
        youtube_response = youtube_client.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            maxResults=top_level_limit,
            order='relevance'  # Most relevant comments first
        ).execute()
        
        if not youtube_response.get('items'):
            return {"comments": []}
        
        for item in youtube_response['items']:
            # Process top-level comment
            top_level_comment = _process_youtube_comment(item['snippet']['topLevelComment'], video_id)
            if top_level_comment:
                comments_data.append(top_level_comment)
            
            # Process replies if requested and available
            if include_replies and item.get('replies') and item['replies'].get('comments'):
                replies = item['replies']['comments']
                for reply in replies[:3]:  # Limit replies per comment to 3
                    reply_comment = _process_youtube_comment(reply, video_id, parent_comment_id=top_level_comment['comment_id'])
                    if reply_comment:
                        comments_data.append(reply_comment)
                        
                        # Stop if we've reached our limit
                        if len(comments_data) >= limit:
                            break
                
                # Stop if we've reached our limit
                if len(comments_data) >= limit:
                    break
        
        # Limit to requested number
        comments_data = comments_data[:limit]
        
        return {"comments": comments_data}
        
    except Exception as e:
        logger.error(f"Error fetching comments from YouTube API: {str(e)}")
        return {"error": f"Error fetching comments from YouTube API: {str(e)}"}


def _process_youtube_comment(youtube_comment: dict, video_id: str, parent_comment_id: str = None) -> Dict[str, Any]:
    """Process a single YouTube comment into our format"""
    try:
        snippet = youtube_comment.get('snippet', {})
        
        # Parse published date
        published_at = None
        if snippet.get('publishedAt'):
            try:
                # Parse YouTube's ISO 8601 format: "2023-10-15T14:30:00Z"
                published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Error parsing published date: {e}")
        
        # Parse updated date
        updated_at = None
        if snippet.get('updatedAt'):
            try:
                updated_at = datetime.fromisoformat(snippet['updatedAt'].replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Error parsing updated date: {e}")
        
        return {
            "comment_id": youtube_comment['id'],
            "parent_comment_id": parent_comment_id,
            "author_display_name": snippet.get('authorDisplayName'),
            "author_channel_id": snippet.get('authorChannelId', {}).get('value'),
            "author_profile_image_url": snippet.get('authorProfileImageUrl'),
            "text_display": snippet.get('textDisplay'),
            "text_original": snippet.get('textOriginal'),
            "like_count": snippet.get('likeCount', 0),
            "published_at": published_at,
            "updated_at": updated_at,
            "is_reply": parent_comment_id is not None,
            "reply_count": 0  # We'll calculate this if needed
        }
        
    except Exception as e:
        logger.error(f"Error processing YouTube comment: {str(e)}")
        return None


def _save_comments_to_database(
    video_id: str, 
    comments_data: Dict[str, Any], 
    user_id: UUID, 
    db: Session
) -> List[VideoComment]:
    """Helper function to save comments to database"""
    saved_comments = []
    
    for comment_data in comments_data.get("comments", []):
        try:
            # Check if comment already exists for this user
            statement = select(VideoComment).where(
                VideoComment.video_id == video_id,
                VideoComment.user_id == user_id,
                VideoComment.comment_id == comment_data['comment_id']
            )
            existing_comment = db.exec(statement).first()
            
            if existing_comment:
                # Update existing comment
                existing_comment.text_display = comment_data['text_display']
                existing_comment.text_original = comment_data['text_original']
                existing_comment.like_count = comment_data['like_count']
                existing_comment.updated_at = comment_data['updated_at']
                existing_comment.updated_at_local = datetime.utcnow()
                
                db.add(existing_comment)
                saved_comments.append(existing_comment)
                logger.debug(f"Updated existing comment {comment_data['comment_id']}")
            else:
                # Create new comment
                new_comment = VideoComment(
                    video_id=video_id,
                    user_id=user_id,
                    comment_id=comment_data['comment_id'],
                    parent_comment_id=comment_data['parent_comment_id'],
                    author_display_name=comment_data['author_display_name'],
                    author_channel_id=comment_data['author_channel_id'],
                    author_profile_image_url=comment_data['author_profile_image_url'],
                    text_display=comment_data['text_display'],
                    text_original=comment_data['text_original'],
                    like_count=comment_data['like_count'],
                    published_at=comment_data['published_at'],
                    updated_at=comment_data['updated_at'],
                    is_reply=comment_data['is_reply'],
                    reply_count=comment_data['reply_count']
                )
                
                db.add(new_comment)
                saved_comments.append(new_comment)
                logger.debug(f"Created new comment {comment_data['comment_id']}")
                
        except Exception as e:
            logger.error(f"Error saving comment {comment_data.get('comment_id', 'unknown')}: {str(e)}")
            continue
    
    try:
        db.commit()
        logger.info(f"Successfully saved {len(saved_comments)} comments to database")
    except Exception as e:
        logger.error(f"Error committing comments to database: {str(e)}")
        db.rollback()
        return []
    
    return saved_comments

