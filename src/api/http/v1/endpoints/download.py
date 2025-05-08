from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from src.api.http.dependencies import security
from src.core.connections.database.postgres_connection import postgres
from src.models.download_model import DownloadModel

router = APIRouter(prefix="/download", tags=["download"])

@router.post("/log")
@router.post("/log")
async def log_download(
    video_id: int,
    result: str,           # "REAL" or "FAKE"
    confidence: float,     # 0.87, etc.
    user=Depends(security.access_token_required),
):
    async with postgres.connection_pool_factory()() as session:
        download = DownloadModel(
            user_id=user.sub,
            video_id=video_id,
            result=result.upper(),
            confidence=confidence
        )
        session.add(download)
        await session.commit()
        return {"status": "ok"}

@router.get("/count")
async def get_download_count(user=Depends(security.access_token_required)):
    async with postgres.connection_pool_factory()() as session:
        result = await session.execute(
            select(func.count()).select_from(DownloadModel).where(DownloadModel.user_id == user.sub)
        )
        count = result.scalar()
        return {"count": count}

@router.get("/history")
async def get_download_history(user=Depends(security.access_token_required)):
    async with postgres.connection_pool_factory()() as session:
        result = await session.execute(
            select(DownloadModel).where(DownloadModel.user_id == user.sub).order_by(DownloadModel.timestamp.desc())
        )
        downloads = result.scalars().all()
        return [
            {
                "video_id": d.video_id,
                "result": d.result,
                "confidence": d.confidence,
                "timestamp": d.timestamp
            } for d in downloads
        ]