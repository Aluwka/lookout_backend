from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, String, ForeignKey, Column
from sqlalchemy.sql import func  # ✅ add this
from datetime import datetime
from .base_model import BaseModel


class DownloadModel(Base):
    __tablename__ = "downloads"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, nullable=False)
    video_id = mapped_column(Integer, nullable=False)
    result = mapped_column(String, nullable=False)
    confidence = mapped_column(Float, nullable=False)
    file_name = mapped_column(String, nullable=True)  # ✅ already included
    download_count = mapped_column(Integer, default=0)  # ✅ already included
    timestamp = mapped_column(DateTime, server_default=func.now(), nullable=False)
