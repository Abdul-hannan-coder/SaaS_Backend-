from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from uuid import UUID

from .controller import get_video_comments_controller, delete_comment_controller, reply_to_comment_controller, reply_to_multiple_comments_controller, CommentsControllerResponse, generate_ai_replies_controller
from .model import GetCommentsRequest, DeleteCommentResponse, ReplyCommentRequest, ReplyMultipleCommentsRequest, ReplyCommentResponse, ReplyCommentsResponse, ReplyGenerationRequest, ReplyGenerationResponse, GeneratedReply, CommentInput
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp

router = APIRouter(prefix="/comments", tags=["Video Comments"])


@router.get("/{video_id}", response_model=CommentsControllerResponse)
async def get_video_comments(
    video_id: str,
    limit: int = Query(default=20, ge=1, le=100, description="Number of comments to retrieve (1-100)"),
    refresh: bool = Query(default=False, description="If true, fetch fresh data from YouTube API"),
    include_replies: bool = Query(default=True, description="Include comment replies"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get comments for a specific video
    
    Args:
        video_id: YouTube video ID
        limit: Number of comments to retrieve (1-100, default: 20)
        refresh: If True, fetch fresh data from YouTube API and update database
                If False, return data from database cache
        include_replies: Include comment replies in the response
    
    Returns: List of comments with author info, text, likes, and metadata
    """
    return get_video_comments_controller(
        video_id=video_id,
        user_id=current_user.id,
        db=db,
        limit=limit,
        refresh=refresh,
        include_replies=include_replies
    )


@router.delete("/{comment_id}", response_model=DeleteCommentResponse)
async def delete_comment(
    comment_id: str,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    ⚠️ PERMANENTLY DELETE a comment from YouTube for the authenticated user
    
    Args:
        comment_id: YouTube comment ID
    
    Returns: success status and deleted comment ID
    
    WARNING: This action is IRREVERSIBLE! The comment will be permanently deleted from YouTube.
    Only comments posted by the authenticated user can be deleted.
    """
    return delete_comment_controller(
        comment_id=comment_id,
        user_id=current_user.id,
        db=db
    )


@router.post("/reply", response_model=ReplyCommentResponse)
async def reply_to_comment(
    reply_request: ReplyCommentRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Reply to a single comment on YouTube
    
    Args:
        reply_request: Contains parent_comment_id and reply_text
    
    Returns: Reply details with success status
    """
    return reply_to_comment_controller(
        parent_comment_id=reply_request.parent_comment_id,
        reply_text=reply_request.reply_text,
        user_id=current_user.id,
        db=db
    )


@router.post("/reply-multiple", response_model=ReplyCommentsResponse)
async def reply_to_multiple_comments(
    reply_request: ReplyMultipleCommentsRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Reply to multiple comments on YouTube (1-10 replies at once)
    
    Args:
        reply_request: Contains list of replies with parent_comment_id and reply_text
    
    Returns: Summary of all replies with individual success/failure status
    """
    return reply_to_multiple_comments_controller(
        replies=reply_request.replies,
        user_id=current_user.id,
        db=db
    )


@router.post("/generate-ai-replies", response_model=ReplyGenerationResponse)
async def generate_ai_replies(
    request: ReplyGenerationRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Generate AI-powered replies for comments
    
    This endpoint generates thoughtful, context-aware replies to video comments
    using the video transcript as context. The AI agent can handle multiple
    comments and adapt the reply style based on your preferences.
    
    Args:
        request: Contains comment_ids OR comment_texts, video_id, reply_style, and max_length
    
    Returns: List of generated replies with confidence scores
    """
    return await generate_ai_replies_controller(
        request=request,
        user_id=current_user.id,
        db=db
    )
