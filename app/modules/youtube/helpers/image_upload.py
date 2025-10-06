from sqlmodel import Session
from uuid import uuid4
from fastapi import UploadFile
from ..thumbnail_generator.error_models import (
    ValidationError,
    DatabaseError
)
from ....utils.my_logger import get_logger
from pathlib import Path

logger = get_logger("IMAGE_UPLOAD")

async def upload_custom_thumbnail(
    video_id: str,
    file_content:UploadFile ,
    dir_path: str,
    db: Session

) -> dict:
    """
    Upload and save a custom thumbnail file
    """
    # Validate file
    if not file_content.file:
        raise ValidationError("File content cannot be empty", field="file", error_type="missing_file")

    # if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
    #     raise ValidationError("File size must be less than 10MB", field="file", error_type="file_too_large")
    
    filename = f"{video_id}.png"
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError("File must be an image (jpg, jpeg, png, gif, webp)", field="file", error_type="invalid_file_type")
   
    # Save file and update database
    try:        
       
        # Create thumbnails directory if it doesn't exist
        thumbnails_dir = Path(dir_path)
        thumbnails_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        
        filepath = thumbnails_dir / filename
        
        # Save file
        with open(filepath, 'wb') as f:
            content = await file_content.read()
            f.write(content)
        
               
        return {
            "success": True,
            "message": "Custom thumbnail uploaded successfully",
            "custom_thumbnail_path": str(filepath),
            "filename": filename,
            "video_id": video_id,
            "thumbnail_url": str(filepath),
            "method_used": "custom_upload"
        }
        
    except Exception as e:
        db.rollback()
        # Clean up file if it was created
        if 'filepath' in locals() and filepath.exists():
            filepath.unlink()
        raise DatabaseError(f"Error uploading thumbnail: {str(e)}", operation="upload_custom_thumbnail", error_type="transaction")


