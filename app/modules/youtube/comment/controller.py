"""
Controller layer for video comments
"""
from typing import Dict, Any, List
from uuid import UUID
from sqlmodel import Session
from pydantic import BaseModel

from .service import get_video_comments_service, delete_comment_service, reply_to_comment_service, reply_to_multiple_comments_service, generate_ai_replies_service
from .model import CommentsControllerResponse, GetCommentsRequest, DeleteCommentResponse, ReplyCommentRequest, ReplyMultipleCommentsRequest, ReplyCommentResponse, ReplyCommentsResponse, ReplyGenerationRequest, ReplyGenerationResponse, GeneratedReply, CommentInput
from ....utils.my_logger import get_logger

logger = get_logger("VIDEO_COMMENTS_CONTROLLER")


class CommentsControllerResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]


def get_video_comments_controller(
    video_id: str, 
    user_id: UUID, 
    db: Session, 
    limit: int = 20, 
    refresh: bool = False,
    include_replies: bool = True
) -> CommentsControllerResponse:
    """Get comments for a video by video ID for a specific user"""
    result = get_video_comments_service(video_id, user_id, db, limit, refresh, include_replies)
    
    return CommentsControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result["data"].dict() if result["data"] else None
    )


def delete_comment_controller(
    comment_id: str, 
    user_id: UUID, 
    db: Session
) -> DeleteCommentResponse:
    """Delete a comment by comment ID for a specific user"""
    result = delete_comment_service(comment_id, user_id, db)
    
    return DeleteCommentResponse(
        success=result["success"],
        message=result["message"],
        deleted_comment_id=result["deleted_comment_id"]
    )


def reply_to_comment_controller(
    parent_comment_id: str,
    reply_text: str,
    user_id: UUID,
    db: Session
) -> ReplyCommentResponse:
    """Reply to a single comment for a specific user"""
    result = reply_to_comment_service(parent_comment_id, reply_text, user_id, db)
    
    return ReplyCommentResponse(
        parent_comment_id=result["parent_comment_id"],
        reply_comment_id=result["reply_comment_id"],
        reply_text=result["reply_text"],
        success=result["success"],
        message=result["message"]
    )


def reply_to_multiple_comments_controller(
    replies: List[ReplyCommentRequest],
    user_id: UUID,
    db: Session
) -> ReplyCommentsResponse:
    """Reply to multiple comments for a specific user"""
    result = reply_to_multiple_comments_service(replies, user_id, db)
    
    return ReplyCommentsResponse(
        success=result["success"],
        message=result["message"],
        total_replies_attempted=result["total_replies_attempted"],
        successful_replies=result["successful_replies"],
        failed_replies=result["failed_replies"],
        replies=result["replies"]
    )


async def generate_ai_replies_controller(
    request: ReplyGenerationRequest,
    user_id: UUID,
    db: Session
) -> ReplyGenerationResponse:
    """Generate AI replies for comments"""
    return await generate_ai_replies_service(
        comments=[{"comment_id": comment.comment_id, "comment_text": comment.comment_text} for comment in request.comments],
        user_id=user_id,
        db=db
    )
