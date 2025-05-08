from pydantic import BaseModel, Field, FileUrl
from .mixins.id_mixin import IDMixin
from .mixins.time_mixin import TimeMixin
from typing import Optional


class VideoBase(BaseModel):
    """
    Base schema for video.
    """
    user_id: int = Field(..., description="ID of the user who uploaded the video")
    file_url: str = Field(..., description="URL of the video file")
    file_name: Optional[str] = Field(None, description="Original name of the uploaded file")

    class Config:
        from_attributes = True


class VideoCreate(VideoBase):
    """
    Schema for creating a new video entry.
    """
    pass

class VideoUpdate(VideoCreate):
    """
    Schema for updating an existing video entry.
    """
    pass

class VideoResponse(VideoCreate, IDMixin, TimeMixin):
    """
    Schema for responding with video entry details.
    """