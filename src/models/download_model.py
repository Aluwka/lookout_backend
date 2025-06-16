from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, String, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from .base_model import BaseModel

class DownloadModel(BaseModel):
    __tablename__ = "downloads"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    result: Mapped[str] = mapped_column(String(10), nullable=False, default="FAKE")
    confidence: Mapped[float] = mapped_column(nullable=False, default=0.0)
    file_name: Mapped[str] = mapped_column(String(255), nullable=True, default="")  # ✅ Added
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # ✅ Added
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
