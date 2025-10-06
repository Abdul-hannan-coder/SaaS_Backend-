from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import LONGTEXT
from uuid import UUID
from pydantic import BaseModel


class DashboardOverviewDetails(SQLModel, table=True):
    """Model for dashboard overview details - database table"""
    __tablename__ = "dashboard_overview_details"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Basic Channel Metrics
    total_videos: Optional[int] = Field(default=None)
    total_views: Optional[int] = Field(default=None)
    subscriber_count: Optional[int] = Field(default=None)
    engagement_rate: Optional[float] = Field(default=None)
    
    # Monetization Progress
    watch_time_hours: Optional[float] = Field(default=None)
    monetization_eligible: Optional[bool] = Field(default=None)
    subscriber_progress_percentage: Optional[float] = Field(default=None)
    watch_time_progress_percentage: Optional[float] = Field(default=None)
    
    # Content Distribution Analytics (JSON fields)
    content_type_distribution: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    view_distribution: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    video_duration_distribution: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    engagement_distribution: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    
    # Monthly Analytics Overview (JSON field)
    monthly_analytics: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    
    # Top Performance Content (JSON field)
    top_performance_content: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))
    
    # Performance Metrics from Image
    avg_views_per_video: Optional[float] = Field(default=None)
    avg_likes_per_video: Optional[float] = Field(default=None)
    avg_comments_per_video: Optional[float] = Field(default=None)
    avg_duration: Optional[float] = Field(default=None)
    
    # Channel Status
    engagement_level: Optional[str] = Field(default=None, max_length=50)
    content_quality: Optional[str] = Field(default=None, max_length=50)
    upload_consistency: Optional[str] = Field(default=None, max_length=50)
    growth_potential: Optional[str] = Field(default=None, max_length=50)
    
    # Growth Insights
    channel_age: Optional[float] = Field(default=None)  # in months
    upload_frequency: Optional[float] = Field(default=None)  # videos per month
    total_watch_time: Optional[float] = Field(default=None)  # in hours
    health_score: Optional[float] = Field(default=None)  # out of 100
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Add unique constraint for user_id
    __table_args__ = (
        {"extend_existing": True}
    )


class DashboardOverviewResponse(BaseModel):
    """Response model for dashboard overview"""
    
    # Basic Channel Metrics
    total_videos: Optional[int] = None
    total_views: Optional[int] = None
    subscriber_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    
    # Monetization Progress
    monetization_progress: Optional[Dict[str, Any]] = None
    
    # Content Distribution Analytics
    content_type_distribution: Optional[Dict[str, Any]] = None
    view_distribution: Optional[Dict[str, Any]] = None
    video_duration_distribution: Optional[Dict[str, Any]] = None
    engagement_distribution: Optional[Dict[str, Any]] = None
    
    # Monthly Analytics Overview
    monthly_analytics: Optional[Dict[str, Any]] = None
    
    # Top Performance Content
    top_performance_content: Optional[Dict[str, Any]] = None
    
    # Performance Metrics
    performance_metrics: Optional[Dict[str, Any]] = None
    
    # Channel Status
    channel_status: Optional[Dict[str, Any]] = None
    
    # Growth Insights
    growth_insights: Optional[Dict[str, Any]] = None


class DashboardOverviewControllerResponse(BaseModel):
    """Controller response model for dashboard overview"""
    success: bool
    message: str
    data: Dict[str, Any]
    refreshed: bool = False
