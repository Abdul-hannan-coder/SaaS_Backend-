import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from ..video.model import Video
from ....utils.database_dependency import get_database_session
from ....utils.my_logger import get_logger

logger = get_logger("VIDEO_CLEANUP")

class VideoCleanupService:
    def __init__(self):
        self.cleanup_tasks = {}  # Store cleanup tasks by video_id
        
    async def schedule_video_cleanup(self, video_id: UUID, video_path: str, db: Session):
        """
        Schedule video cleanup after 30 minutes
        """
        try:
            # Cancel existing task if any
            if video_id in self.cleanup_tasks:
                self.cleanup_tasks[video_id].cancel()
            
            # Create new cleanup task
            task = asyncio.create_task(self._cleanup_video_after_delay(video_id, video_path, db))
            self.cleanup_tasks[video_id] = task
            
            logger.info(f"Scheduled cleanup for video {video_id} in 30 minutes")
            
        except Exception as e:
            logger.error(f"Error scheduling cleanup for video {video_id}: {e}")
    
    async def _cleanup_video_after_delay(self, video_id: UUID, video_path: str, db: Session):
        """
        Wait 30 minutes then cleanup video
        """
        try:
            # Wait 30 minutes
            await asyncio.sleep(30 * 60)  # 30 minutes in seconds
            
            # Cleanup video
            await self._cleanup_video(video_id, video_path, db)
            
        except asyncio.CancelledError:
            logger.info(f"Cleanup task cancelled for video {video_id}")
        except Exception as e:
            logger.error(f"Error in cleanup task for video {video_id}: {e}")
        finally:
            # Remove task from tracking
            if video_id in self.cleanup_tasks:
                del self.cleanup_tasks[video_id]
    
    async def _cleanup_video(self, video_id: UUID, video_path: str, db: Session):
        """
        Remove video from database and file system
        """
        try:
            # Remove from database
            statement = select(Video).where(Video.id == video_id)
            video = db.exec(statement).first()
            
            if video:
                db.delete(video)
                db.commit()
                logger.info(f"Removed video {video_id} from database")
            
            # Remove file from filesystem
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"Removed video file: {video_path}")
            else:
                logger.warning(f"Video file not found: {video_path}")
                
        except Exception as e:
            logger.error(f"Error cleaning up video {video_id}: {e}")
            db.rollback()
    
    def cancel_cleanup(self, video_id: UUID):
        """
        Cancel scheduled cleanup for a video
        """
        if video_id in self.cleanup_tasks:
            self.cleanup_tasks[video_id].cancel()
            del self.cleanup_tasks[video_id]
            logger.info(f"Cancelled cleanup for video {video_id}")
    
    def get_active_cleanups(self) -> list:
        """
        Get list of active cleanup tasks
        """
        return list(self.cleanup_tasks.keys())

# Global instance
video_cleanup_service = VideoCleanupService() 