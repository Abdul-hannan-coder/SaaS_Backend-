"""
All-in-one video processing service
"""
import asyncio
import time
from typing import Dict, Any, List
from uuid import UUID
from sqlmodel import Session

from .model import AllInOneRequest, AllInOneResponse, TitleResult, DescriptionResult, TimestampsResult, ThumbnailsResult, SaveContentRequest, SaveContentResponse
from ..title_generator.service import generate_video_title
from ..discription_generator.service import generate_video_description
from ..timestamps_generator.service import generate_video_timestamps
from ..helpers.thumbnail_generation import generate_video_thumbnail
from ..helpers.transcript_dependency import get_video_transcript
from ..gemini.service import get_user_gemini_api_key
from ..helpers.download_image_from_url import download_image_from_url
from ..video.model import Video
from sqlmodel import select
from ....utils.my_logger import get_logger

logger = get_logger("ALL_IN_ONE_SERVICE")


async def process_video_all_in_one(
    request: AllInOneRequest,
    user_id: UUID,
    db: Session
) -> AllInOneResponse:
    """
    Process a video with all available generation features
    """
    start_time = time.time()
    
    try:
        logger.info(f"🚀 Starting all-in-one processing for video {request.video_id}")
        
        # Convert video_id to UUID for internal processing
        try:
            video_uuid = UUID(request.video_id)
        except ValueError:
            # If not a UUID, treat as YouTube video ID
            video_uuid = None
        
        # Initialize results
        results = {}
        errors = []
        completed_tasks = 0
        total_tasks = 0
        
        # Always generate all features
        total_tasks = 4
        
        logger.info(f"📊 Total tasks to process in parallel: {total_tasks}")
        
        # Get Gemini API key for services that need it
        api_key = get_user_gemini_api_key(user_id, db)
        
        # Get transcript once for thumbnail generation
        transcript = "No transcript available"
        try:
            transcript = get_video_transcript(video_uuid or UUID("00000000-0000-0000-0000-000000000001"), user_id, db)
            if not transcript:
                logger.warning("No transcript available for thumbnail generation")
                transcript = "No transcript available"
        except Exception as e:
            logger.warning(f"Could not get transcript for thumbnail generation: {str(e)}")
            transcript = "No transcript available"
        
        # Define helper functions for each task
        async def generate_titles_task():
            try:
                logger.info("📝 Starting title generation...")
                title_result = await generate_video_title(
                    video_id=video_uuid or UUID("00000000-0000-0000-0000-000000000001"),
                    user_id=user_id,
                    db=db,
                    user_requirements=None,
                    api_key=api_key
                )
                logger.info("✅ Title generation completed")
                return TitleResult(
                    success=title_result.success,
                    message=title_result.message,
                    generated_titles=title_result.generated_titles
                )
            except Exception as e:
                error_msg = f"Title generation failed: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return TitleResult(
                    success=False,
                    message=error_msg,
                    generated_titles=[],
                    error=error_msg
                )
        
        async def generate_description_task():
            try:
                logger.info("📄 Starting description generation...")
                description_result = await generate_video_description(
                    video_id=video_uuid or UUID("00000000-0000-0000-0000-000000000001"),
                    user_id=user_id,
                    db=db,
                    custom_template=None
                )
                logger.info("✅ Description generation completed")
                return DescriptionResult(
                    success=description_result["success"],
                    message=description_result["message"],
                    generated_description=description_result.get("generated_description")
                )
            except Exception as e:
                error_msg = f"Description generation failed: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return DescriptionResult(
                    success=False,
                    message=error_msg,
                    error=error_msg
                )
        
        async def generate_timestamps_task():
            try:
                logger.info("⏰ Starting timestamps generation...")
                timestamps_result = await generate_video_timestamps(
                    video_id=video_uuid or UUID("00000000-0000-0000-0000-000000000001"),
                    user_id=user_id,
                    db=db
                )
                
                # Handle timestamps result - convert string to list if needed
                generated_timestamps = timestamps_result.get("generated_timestamps")
                if isinstance(generated_timestamps, str):
                    # Convert string timestamps to list format
                    timestamp_lines = generated_timestamps.strip().split('\n')
                    generated_timestamps = []
                    for line in timestamp_lines:
                        if line.strip() and ' ' in line:
                            parts = line.split(' ', 1)
                            if len(parts) == 2:
                                generated_timestamps.append({
                                    "time": parts[0].strip(),
                                    "title": parts[1].strip()
                                })
                
                logger.info("✅ Timestamps generation completed")
                return TimestampsResult(
                    success=timestamps_result["success"],
                    message=timestamps_result["message"],
                    generated_timestamps=generated_timestamps
                )
            except Exception as e:
                error_msg = f"Timestamps generation failed: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return TimestampsResult(
                    success=False,
                    message=error_msg,
                    error=error_msg
                )
        
        async def generate_thumbnails_task():
            try:
                logger.info("🖼️ Starting thumbnail generation (5 thumbnails)...")
                
                # Generate 5 different thumbnails concurrently
                thumbnail_tasks = []
                for i in range(5):
                    async def generate_single_thumbnail(thumbnail_id):
                        try:
                            logger.info(f"🖼️ Generating thumbnail {thumbnail_id}/5...")
                            thumbnail_result = await generate_video_thumbnail(
                                video_id=video_uuid or UUID("00000000-0000-0000-0000-000000000001"),
                                user_id=user_id,
                                db=db,
                                transcript=transcript
                            )
                            
                            if thumbnail_result.get("success") and thumbnail_result.get("image_url"):
                                logger.info(f"✅ Thumbnail {thumbnail_id}/5 generated successfully")
                                return {
                                    "thumbnail_id": thumbnail_id,
                                    "image_url": thumbnail_result["image_url"],
                                    "success": True
                                }
                            else:
                                logger.warning(f"⚠️ Thumbnail {thumbnail_id}/5 failed")
                                return {
                                    "thumbnail_id": thumbnail_id,
                                    "image_url": None,
                                    "success": False,
                                    "error": thumbnail_result.get("message", "Failed to generate")
                                }
                        except Exception as e:
                            logger.warning(f"⚠️ Thumbnail {thumbnail_id}/5 failed: {str(e)}")
                            return {
                                "thumbnail_id": thumbnail_id,
                                "image_url": None, 
                                "success": False,
                                "error": str(e)
                            }
                    
                    thumbnail_tasks.append(generate_single_thumbnail(i + 1))
                
                # Run all thumbnail generations in parallel
                generated_thumbnails = await asyncio.gather(*thumbnail_tasks)
                successful_thumbnails = sum(1 for thumb in generated_thumbnails if thumb["success"])
                
                # Determine overall success
                overall_success = successful_thumbnails > 0
                message = f"Generated {successful_thumbnails}/5 thumbnails successfully"
                
                logger.info("✅ Thumbnails generation completed")
                return ThumbnailsResult(
                    success=overall_success,
                    message=message,
                    generated_thumbnails=generated_thumbnails
                )
            except Exception as e:
                error_msg = f"Thumbnails generation failed: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return ThumbnailsResult(
                    success=False,
                    message=error_msg,
                    error=error_msg
                )
        
        # Run all main tasks in parallel
        logger.info("🚀 Starting parallel execution of all tasks...")
        task_results = await asyncio.gather(
            generate_titles_task(),
            generate_description_task(),
            generate_timestamps_task(),
            generate_thumbnails_task(),
            return_exceptions=True
        )
        
        # Process results
        results["titles"] = task_results[0] if not isinstance(task_results[0], Exception) else TitleResult(
            success=False, message=f"Exception: {str(task_results[0])}", generated_titles=[], error=str(task_results[0])
        )
        results["description"] = task_results[1] if not isinstance(task_results[1], Exception) else DescriptionResult(
            success=False, message=f"Exception: {str(task_results[1])}", error=str(task_results[1])
        )
        results["timestamps"] = task_results[2] if not isinstance(task_results[2], Exception) else TimestampsResult(
            success=False, message=f"Exception: {str(task_results[2])}", error=str(task_results[2])
        )
        results["thumbnails"] = task_results[3] if not isinstance(task_results[3], Exception) else ThumbnailsResult(
            success=False, message=f"Exception: {str(task_results[3])}", error=str(task_results[3])
        )
        
        # Count completed tasks
        completed_tasks = sum(1 for result in task_results if not isinstance(result, Exception) and result.success)
        errors = [str(result) for result in task_results if isinstance(result, Exception)]
        
        # Calculate processing time
        processing_time = time.time() - start_time
        failed_tasks = total_tasks - completed_tasks
        
        # Determine overall success
        overall_success = completed_tasks > 0 and failed_tasks == 0
        
        message = f"All-in-one processing completed: {completed_tasks}/{total_tasks} tasks successful"
        if failed_tasks > 0:
            message += f", {failed_tasks} failed"
        
        logger.info(f"🎉 {message} in {processing_time:.2f} seconds")
        
        return AllInOneResponse(
            success=overall_success,
            message=message,
            video_id=request.video_id,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            results=results,
            processing_time_seconds=processing_time,
            errors=errors
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"All-in-one processing failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return AllInOneResponse(
            success=False,
            message=error_msg,
            video_id=request.video_id,
            total_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            results={},
            processing_time_seconds=processing_time,
            errors=[error_msg]
        )


async def save_generated_content(
    request: SaveContentRequest,
    video_id: str,
    user_id: UUID,
    db: Session
) -> SaveContentResponse:
    """
    Save selected generated content (title, thumbnail, description, timestamps) to video record
    """
    try:
        logger.info(f"💾 Saving generated content for video {video_id}")
        
        # Convert video_id to UUID for internal processing
        try:
            video_uuid = UUID(video_id)
        except ValueError:
            # If not a UUID, treat as YouTube video ID
            video_uuid = None
        
        # Check if video exists
        statement = select(Video).where(
            Video.id == video_uuid,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            return SaveContentResponse(
                success=False,
                message="Video not found",
                video_id=video_id,
                saved_content={},
                thumbnail_path=None
            )
        
        saved_content = {}
        thumbnail_path = None
        
        # Save selected title
        if request.selected_title:
            try:
                video.title = request.selected_title.strip()
                saved_content["title"] = request.selected_title.strip()
                logger.info(f"✅ Title saved: {request.selected_title[:50]}...")
            except Exception as e:
                logger.error(f"❌ Failed to save title: {str(e)}")
        
        # Download and save selected thumbnail
        if request.selected_thumbnail_url:
            try:
                logger.info(f"📥 Downloading thumbnail from: {request.selected_thumbnail_url}")
                thumbnail_result = await download_image_from_url(
                    url=request.selected_thumbnail_url,
                    dir_path="thumbnails",
                    video_id=video_uuid
                )
                
                video.thumbnail_url = request.selected_thumbnail_url
                video.thumbnail_path = thumbnail_result["custom_thumbnail_path"]
                thumbnail_path = thumbnail_result["custom_thumbnail_path"]
                saved_content["thumbnail"] = {
                    "url": request.selected_thumbnail_url,
                    "path": thumbnail_result["custom_thumbnail_path"]
                }
                logger.info(f"✅ Thumbnail downloaded and saved: {thumbnail_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to download/save thumbnail: {str(e)}")
                saved_content["thumbnail"] = {"error": str(e)}
        
        # Save description (if provided)
        if request.description:
            try:
                video.description = request.description.strip()
                saved_content["description"] = request.description.strip()
                logger.info(f"✅ Description saved: {request.description[:50]}...")
            except Exception as e:
                logger.error(f"❌ Failed to save description: {str(e)}")
        
        # Save timestamps (if provided)
        if request.timestamps:
            try:
                # Convert timestamps list to JSON string for database storage
                import json
                video.timestamps = json.dumps(request.timestamps)
                saved_content["timestamps"] = request.timestamps
                logger.info(f"✅ Timestamps saved: {len(request.timestamps)} timestamp entries")
            except Exception as e:
                logger.error(f"❌ Failed to save timestamps: {str(e)}")
        
        # Save privacy status (if provided)
        if request.privacy_status:
            try:
                video.privacy_status = request.privacy_status.strip()
                saved_content["privacy_status"] = request.privacy_status.strip()
                logger.info(f"✅ Privacy status saved: {request.privacy_status}")
            except Exception as e:
                logger.error(f"❌ Failed to save privacy status: {str(e)}")
        
        # Save playlist name (if provided)
        if request.playlist_name:
            try:
                video.playlist_name = request.playlist_name.strip()
                saved_content["playlist_name"] = request.playlist_name.strip()
                logger.info(f"✅ Playlist name saved: {request.playlist_name}")
            except Exception as e:
                logger.error(f"❌ Failed to save playlist name: {str(e)}")
        
        # Save schedule datetime (if provided)
        if request.schedule_datetime:
            try:
                from datetime import datetime
                # Parse ISO format datetime string
                schedule_dt = datetime.fromisoformat(request.schedule_datetime.replace('Z', '+00:00'))
                video.schedule_datetime = schedule_dt
                saved_content["schedule_datetime"] = request.schedule_datetime
                logger.info(f"✅ Schedule datetime saved: {request.schedule_datetime}")
            except Exception as e:
                logger.error(f"❌ Failed to save schedule datetime: {str(e)}")
                saved_content["schedule_datetime"] = {"error": str(e)}
        
        # Commit all changes to database
        try:
            db.add(video)
            db.commit()
            
            success_message = f"Successfully saved content for video {video_id}"
            if saved_content:
                success_message += f" - Saved: {', '.join(saved_content.keys())}"
            
            logger.info(f"🎉 {success_message}")
            
            return SaveContentResponse(
                success=True,
                message=success_message,
                video_id=video_id,
                saved_content=saved_content,
                thumbnail_path=thumbnail_path
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Database error while saving content: {str(e)}")
            return SaveContentResponse(
                success=False,
                message=f"Database error: {str(e)}",
                video_id=video_id,
                saved_content=saved_content,
                thumbnail_path=None
            )
        
    except Exception as e:
        logger.error(f"❌ Error saving generated content: {str(e)}")
        return SaveContentResponse(
            success=False,
            message=f"Error saving content: {str(e)}",
            video_id=video_id,
            saved_content={},
            thumbnail_path=None
        )
