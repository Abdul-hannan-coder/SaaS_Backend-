from fastapi import APIRouter, Depends, HTTPException,Query
from sqlmodel import Session
from uuid import UUID

from .controller import get_dashboard_overview_controller, get_dashboard_videos_controller, DashboardOverviewControllerResponse
from ....utils.database_dependency import get_database_session
from ....modules.login_logout.controllers.user_controller import get_current_user
from ....modules.login_logout.models.user_model import UserSignUp

router = APIRouter(prefix="/dashboard-overview", tags=["Dashboard Overview"])


@router.get("/", response_model=DashboardOverviewControllerResponse)
async def get_dashboard_overview(
    refresh: bool = False,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get comprehensive dashboard overview data for the authenticated user
    
    This endpoint provides a complete overview of the YouTube channel including:
    
    **Basic Channel Metrics:**
    - Total videos count
    - Total views across all videos  
    - Subscriber count
    - Overall engagement rate
    
    **Monetization Progress:**
    - Current watch time hours
    - Monetization eligibility status
    - Progress towards subscriber requirement (1000 subs)
    - Progress towards watch time requirement (4000 hours)
    
    **Content Distribution Analytics:**
    - Content type distribution (shorts, medium, long videos)
    - View distribution across different view ranges
    - Video duration distribution
    - Engagement distribution across different engagement rates
    
    **Monthly Analytics Overview:**
    - Views, videos, and engagement trends over time
    - Monthly performance data
    - Growth trajectory analysis
    
    **Top Performance Content:**
    - Top videos by views
    - Top videos by likes  
    - Top videos by engagement rate
    - Performance insights and recommendations
    
    **Performance Metrics:**
    - Average views per video
    - Average likes per video
    - Average comments per video
    - Average video duration
    
    **Channel Status:**
    - Engagement level (High/Medium/Low)
    - Content quality assessment
    - Upload consistency rating
    - Growth potential evaluation
    
    **Growth Insights:**
    - Channel age in months
    - Upload frequency (videos per month)
    - Total watch time analysis
    - Overall channel health score (0-100)
    
    Args:
        refresh: If True, fetch fresh data from YouTube API and update database.
                If False, return cached data from database (faster response).
        current_user: The authenticated user from Bearer token
        db: Database session dependency
    
    Returns:
        DashboardOverviewControllerResponse: Complete dashboard overview data
        
    Raises:
        HTTPException: If YouTube API authentication fails or other errors occur
    """
    try:
        return get_dashboard_overview_controller(current_user.id, db, refresh)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving dashboard overview: {str(e)}"
        )


@router.get("/videos", response_model=DashboardOverviewControllerResponse)
async def get_dashboard_videos(
    refresh: bool = False,
    limit: int = Query(50, description="Maximum number of videos to return", ge=1, le=100),
    offset: int = Query(0, description="Number of videos to skip (for pagination)", ge=0),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get all videos for dashboard - fetches from YouTube and stores in single video details table
    
    This endpoint retrieves comprehensive video data for the authenticated user's YouTube channel:
    
    **Video Information:**
    - Video ID, title, and description
    - Thumbnail links and publication dates
    - Privacy status and category information
    - Tags and default language settings
    
    **Performance Metrics:**
    - View count, like count, and comment count
    - Calculated engagement rate per video
    - Video duration and content details
    
    **Data Management:**
    - Fetches all videos from YouTube Data API
    - Stores/updates data in single video details table
    - Supports refresh functionality for fresh data
    - Efficient caching for fast subsequent requests
    
        **API Logic:**
        - If refresh=True: Always fetch fresh data from YouTube API and update database
        - If refresh=False: Return cached data from database if exists, otherwise fetch from YouTube API and save to database
        
        Args:
            refresh: If True, fetch fresh data from YouTube API and update database.
                    If False, return cached data from database (faster response).
            limit: Maximum number of videos to return (1-100, default: 50)
            offset: Number of videos to skip for pagination (default: 0)
            current_user: The authenticated user from Bearer token
            db: Database session dependency
    
    Returns:
        DashboardOverviewControllerResponse: Complete videos data with all video details
        
    Raises:
        HTTPException: If YouTube API authentication fails or other errors occur
    """
    try:
            return get_dashboard_videos_controller(current_user.id, db, refresh, limit, offset)
    except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving dashboard videos: {str(e)}"
            )
