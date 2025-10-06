from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta, timezone
import pytz
from uuid import UUID

class PrivacyStatus(str, Enum):
    """Privacy status options for scheduled videos"""
    PRIVATE = "private"
    PUBLIC = "public"
    UNLISTED = "unlisted"

class ScheduleRequest(BaseModel):
    """Request model for scheduling a video"""
    schedule_date: str = Field(..., description="Schedule date in YYYY-MM-DD format")
    schedule_time: str = Field(..., description="Schedule time in HH:MM format (24-hour)")
    privacy_status: PrivacyStatus = Field(..., description="Privacy status for the scheduled video")
    timezone: Optional[str] = Field(default="UTC", description="Timezone for the schedule time (e.g., 'UTC', 'America/New_York', 'Asia/Karachi')")
    
    @validator('schedule_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @validator('schedule_time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('Time must be in HH:MM format (24-hour)')
    
    def get_schedule_datetime(self) -> str:
        """Convert date and time to ISO datetime string in UTC"""
        datetime_str = f"{self.schedule_date} {self.schedule_time}:00"
        schedule_dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        
        # Convert to the specified timezone, then to UTC
        try:
            if self.timezone == "UTC":
                local_tz = timezone.utc
            else:
                local_tz = pytz.timezone(self.timezone)
            
            # Localize the datetime to the specified timezone
            schedule_dt = local_tz.localize(schedule_dt)
            
            # Convert to UTC
            schedule_dt_utc = schedule_dt.astimezone(timezone.utc)
            
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {self.timezone}")
        
        # Check if time is in the future
        if schedule_dt_utc <= datetime.now(timezone.utc):
            raise ValueError('Schedule time must be in the future')
        
        # Format as ISO string with UTC timezone
        return schedule_dt_utc.isoformat()

class ScheduleResponse(BaseModel):
    """Response model for scheduling"""
    success: bool
    message: str
    data: dict

class ScheduleInfo(BaseModel):
    """Schedule information model"""
    video_id: UUID
    schedule_datetime: str
    privacy_status: str
    video_status: str
    formatted_schedule: str
    time_until_schedule: str 