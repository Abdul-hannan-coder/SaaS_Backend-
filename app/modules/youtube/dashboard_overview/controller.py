"""
Controller layer for dashboard overview
"""
from typing import Dict, Any
from uuid import UUID
from sqlmodel import Session

from .service import get_dashboard_overview_service, get_dashboard_videos_service
from .model import DashboardOverviewControllerResponse
from ....utils.my_logger import get_logger

logger = get_logger("DASHBOARD_OVERVIEW_CONTROLLER")


def get_dashboard_overview_controller(user_id: UUID, db: Session, refresh: bool = False) -> DashboardOverviewControllerResponse:
    """Get dashboard overview data for a specific user"""
    result = get_dashboard_overview_service(user_id, db, refresh)
    
    return DashboardOverviewControllerResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("overview_data", {}),
        refreshed=result.get("refreshed", False)
    )


def get_dashboard_videos_controller(user_id: UUID, db: Session, refresh: bool = False, limit: int = 50, offset: int = 0) -> DashboardOverviewControllerResponse:
    """Get all videos for dashboard for a specific user"""
    result = get_dashboard_videos_service(user_id, db, refresh, limit, offset)
    
    # Combine videos_data and additional_metrics into the response data
    response_data = result.get("videos_data", {})
    if "additional_metrics" in result:
        response_data["additional_metrics"] = result["additional_metrics"]
    
    return DashboardOverviewControllerResponse(
        success=result["success"],
        message=result["message"],
        data=response_data,
        refreshed=result.get("refreshed", False)
    )
