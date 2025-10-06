from fastapi import APIRouter
from sqlmodel import SQLModel
from .utils.my_logger import get_logger

# YouTube Model Imports
from .modules.youtube.youtube_token.model import GoogleToken
from .modules.youtube.dashboard_single_video.model import SingleVideoDetails
from .modules.youtube.dashboard_overview.model import DashboardOverviewDetails
from .modules.youtube.dashboard_playlist.model import UserPlaylist
from .modules.youtube.video.model import Video
from .modules.youtube.gemini.model import GeminiKey
from .modules.youtube.youtube_creds.model import YouTubeCredentials
from .modules.youtube.comment.model import VideoComment

# YouTube Router Imports
from .modules.youtube.youtube_token.route import router as youtube_token_router
from .modules.youtube.video.route import router as video_router
from .modules.youtube.title_generator.route import router as title_generator_router
from .modules.youtube.timestamps_generator.route import router as time_stamps_generator_router
from .modules.youtube.discription_generator.route import router as description_generator_router
from .modules.youtube.thumbnail_generator.route import router as thumbnail_generator_router
from .modules.youtube.gemini.route import router as gemini_key_router
from .modules.youtube.playlist.route import router as playlist_router
from .modules.youtube.privacy_status.route import router as privacy_status_router
from .modules.youtube.schedule.route import router as schedule_router
from .modules.youtube.video_upload.route import router as youtube_upload_router
from .modules.youtube.youtube_creds.route import router as youtube_credentials_router
from .modules.youtube.dashboard_single_video.route import router as single_video_router
from .modules.youtube.dashboard_overview.route import router as dashboard_overview_router
from .modules.youtube.dashboard_playlist.route import router as playlist_route_router
from .modules.youtube.comment.route import router as comment_router
from .modules.youtube.all_in_one.route import router as all_in_one_router


def register_youtube_routes(app):
    """Register all YouTube-related routes with the FastAPI app"""
    # Register all YouTube routers
    app.include_router(youtube_credentials_router)
    app.include_router(youtube_token_router)
    app.include_router(gemini_key_router)
    app.include_router(video_router)
    app.include_router(title_generator_router)
    app.include_router(time_stamps_generator_router)
    app.include_router(description_generator_router)
    app.include_router(thumbnail_generator_router)
    app.include_router(playlist_router)
    app.include_router(privacy_status_router)
    app.include_router(schedule_router)
    app.include_router(youtube_upload_router)
    app.include_router(single_video_router)
    app.include_router(dashboard_overview_router)
    app.include_router(playlist_route_router)
    app.include_router(comment_router)
    app.include_router(all_in_one_router)
    

    get_logger(name="UZAIR").info("✅ All YouTube routes registered successfully")
