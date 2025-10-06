from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import LONGTEXT
from uuid import UUID

class VideoComment(SQLModel, table=True):
    """Model for video comments - database table"""
    __tablename__ = "video_comments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: str = Field(max_length=50, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    comment_id: str = Field(max_length=100, index=True)  # YouTube comment ID
    parent_comment_id: Optional[str] = Field(default=None, max_length=100)  # For replies
    author_display_name: Optional[str] = Field(default=None, max_length=200)
    author_channel_id: Optional[str] = Field(default=None, max_length=100)
    author_profile_image_url: Optional[str] = Field(default=None, max_length=500)
    text_display: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    text_original: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    like_count: Optional[int] = Field(default=0)
    published_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    is_reply: bool = Field(default=False)
    reply_count: Optional[int] = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at_local: datetime = Field(default_factory=datetime.utcnow)
    
    # Add unique constraint for user_id + video_id + comment_id combination
    __table_args__ = (
        {"extend_existing": True}
    )


class CommentResponse(SQLModel):
    """Response model for a single comment"""
    comment_id: str
    parent_comment_id: Optional[str] = None
    author_display_name: Optional[str] = None
    author_channel_id: Optional[str] = None
    author_profile_image_url: Optional[str] = None
    text_display: Optional[str] = None
    text_original: Optional[str] = None
    like_count: Optional[int] = None
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_reply: bool = False
    reply_count: Optional[int] = None


class CommentsListResponse(SQLModel):
    """Response model for comments list"""
    video_id: str
    total_comments: int
    comments: List[CommentResponse]
    limit: int
    refresh: bool = False
    comments_source: Optional[str] = None  # "database" or "youtube"


class CommentsControllerResponse(SQLModel):
    """Controller response wrapper"""
    success: bool
    message: str
    data: CommentsListResponse


class GetCommentsRequest(SQLModel):
    """Request model for getting comments"""
    limit: Optional[int] = Field(default=20, ge=1, le=100)
    refresh: Optional[bool] = Field(default=False)
    include_replies: Optional[bool] = Field(default=True)


class DeleteCommentResponse(SQLModel):
    """Response model for comment deletion"""
    success: bool
    message: str
    deleted_comment_id: Optional[str] = None


class ReplyCommentRequest(SQLModel):
    """Request model for replying to a single comment"""
    parent_comment_id: str = Field(description="YouTube comment ID to reply to")
    reply_text: str = Field(min_length=1, max_length=5000, description="Reply text content")


class ReplyMultipleCommentsRequest(SQLModel):
    """Request model for replying to multiple comments"""
    replies: List[ReplyCommentRequest] = Field(min_items=1, max_items=10, description="List of replies (1-10 replies)")


class ReplyCommentResponse(SQLModel):
    """Response model for a single comment reply"""
    parent_comment_id: str
    reply_comment_id: Optional[str] = None
    reply_text: str
    success: bool
    message: str


class ReplyCommentsResponse(SQLModel):
    """Response model for multiple comment replies"""
    success: bool
    message: str
    total_replies_attempted: int
    successful_replies: int
    failed_replies: int
    replies: List[ReplyCommentResponse]


class CommentInput(SQLModel):
    """Model for a single comment input"""
    comment_id: str = Field(description="Comment ID")
    comment_text: str = Field(description="Comment text content")


class ReplyGenerationRequest(SQLModel):
    """Request model for generating AI replies"""
    comments: List[CommentInput] = Field(min_items=1, max_items=10, description="List of comments with ID and text (1-10 comments)")


class GeneratedReply(SQLModel):
    """Model for a single generated reply"""
    comment_id: str = Field(description="Comment ID or text identifier")
    comment_text: str = Field(description="Original comment text")
    author_name: str = Field(description="Name of the comment author")
    generated_reply: str = Field(description="AI-generated reply text")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")


class ReplyGenerationResponse(SQLModel):
    """Response model for AI-generated replies"""
    success: bool
    message: str
    generated_replies: List[GeneratedReply]
    total_generated: int
