from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.http.dependencies import security
from src.core.connections.database.postgres_connection import postgres
from src.models.download_model import DownloadModel

router = APIRouter(prefix="/download", tags=["download"])
get_db = postgres.get_db


@router.post("/log")
async def log_download(
    video_id: int,
    result: str,
    confidence: float,
    file_name: str = "",  # ✅ accept file name from frontend
    user=Depends(security.access_token_required),
    session: AsyncSession = Depends(postgres.get_db),
):
    # Try to find an existing entry for the same video/user
    result_stmt = await session.execute(
        select(DownloadModel)
        .where(DownloadModel.user_id == int(user.sub))
        .where(DownloadModel.video_id == video_id)
    )
    download = result_stmt.scalars().first()

    if download:
        # increment count if already exists
        download.download_count += 1
    else:
        download = DownloadModel(
            user_id=int(user.sub),
            video_id=video_id,
            result=result,
            confidence=confidence,
            file_name=file_name,
            download_count=1
        )
        session.add(download)

    await session.commit()
    return {"status": "ok"}

@router.get("/count")
async def get_download_count(
    user=Depends(security.access_token_required),
    session: AsyncSession = Depends(get_db),
):
    try:
        user_id = int(user.sub)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    result = await session.execute(
        select(func.count()).select_from(DownloadModel).where(DownloadModel.user_id == user_id)
    )
    return {"count": result.scalar_one() or 0}


@router.get("/history")
async def get_download_history(
    user=Depends(security.access_token_required),
    session: AsyncSession = Depends(get_db),
):
    try:
        user_id = int(user.sub)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    result = await session.execute(
        select(DownloadModel)
        .where(DownloadModel.user_id == user_id)
        .order_by(DownloadModel.timestamp.desc())
    )
    downloads = result.scalars().all()
    return [
        {
            "video_id": d.video_id,
            "result": d.result,
            "confidence": d.confidence,
            "timestamp": d.timestamp,
        }
        for d in downloads
    ]

@router.post("/increment-downloads")
async def increment_download_count(
    video_id: int,
    user=Depends(security.access_token_required),
    session: AsyncSession = Depends(postgres.get_db)
):
    # get the latest download log for this user+video
    result = await session.execute(
        select(DownloadModel)
        .where(DownloadModel.user_id == int(user.sub))
        .where(DownloadModel.video_id == video_id)
        .order_by(DownloadModel.timestamp.desc())
    )
    download = result.scalars().first()
    if download:
        download.download_count = (download.download_count or 0) + 1
        await session.commit()
        return {"status": "updated", "downloads": download.download_count}
    raise HTTPException(status_code=404, detail="Download entry not found")
