from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from .base_model import BaseModel
from .annotations import IDPK, CreatedAt, UpdatedAt

class VideoModel(BaseModel):
    __tablename__ = "videos"

    id: Mapped[IDPK]
    user_id: Mapped[Integer] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_url: Mapped[String] = mapped_column(String(255), nullable=False)
    file_name: Mapped[String] = mapped_column(String(255), nullable=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
