from abc import ABC, abstractmethod
import asyncio
from typing import AsyncGenerator
import tempfile
from src.schemas.model_schema import ModelSchema
from src.schemas.video_schema import VideoCreate
from src.schemas.analysis_result_schema import AnalysisResultCreate, AnalysisResultUpdate
from src.core.storage.storage import Storage
from src.core.storage.s3_storage import s3_storage
from src.repo.video_repo import video_repository
from src.repo.analysis_result_repo import analysis_result_repository
from .repository import Repository
from io import BytesIO
from src.inference.model_inference import ModelInference, model_inference
import tempfile
import yt_dlp, os
import aiohttp
from urllib.parse import urlparse, unquote

MAX_FILE_SIZE_MB = 100
VALID_EXTENSIONS = ['.mp4', '.mov']

async def download_video_from_url(url: str) -> BytesIO:
    try:
        if 'youtube.com' in url or 'youtu.be' in url:
            fd, temp_path = tempfile.mkstemp(suffix=".mp4")
            os.close(fd)  # ❗ Very important: close the open handle

            ydl_opts = {
                'outtmpl': temp_path,
                'format': '18/best[ext=mp4]/best',
                'quiet': True,
                'noplaylist': True,
                'no_warnings': True,
                'verbose': True,
                'overwrites': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
                if result != 0:
                    raise Exception("yt-dlp failed to download the video.")

            print(f"[yt-dlp] Saved file: {temp_path}")
            print(f"[yt-dlp] File size: {os.path.getsize(temp_path)} bytes")

            with open(temp_path, "rb") as f:
                data = f.read()
                if len(data) < 100_000:
                    raise Exception("Downloaded video is too small — likely broken.")
                return BytesIO(data)

        else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise Exception(f"Failed to download video: HTTP {response.status}")
                        content = await response.read()
                        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
                            raise Exception("File is too big. Limit is 100MB.")
                        return BytesIO(content)
    except Exception as e:
        print(f"[download_video_from_url ERROR] {e}")
        raise



class ModelUseCase(ABC):
    @abstractmethod
    async def analyze_video(self, user_id: int, file: BytesIO, file_name: str) -> ModelSchema:
        pass

    @abstractmethod
    async def get_result(self, task_id: str) -> ModelSchema:
        pass

class ModelUseCaseImpl(ModelUseCase):
    def __init__(self, storage: Storage, video_repository: Repository, analysis_result_repository: Repository, model_inference: ModelInference):
        self.storage = storage
        self.video_repository = video_repository
        self.analysis_result_repository = analysis_result_repository
        self.model_inference = model_inference

    async def analyze_video(self, user_id: int, file: BytesIO | str, file_name: str) -> ModelSchema:
        try:
            if isinstance(file, str):
                video_data = await download_video_from_url(file)
                parsed = urlparse(file)
                basename = unquote(parsed.path.split("/")[-1].split("?")[0])
                file_name = basename if basename.endswith((".mp4", ".mov")) else basename + ".mp4"
            else:
                video_data = file

            if not any(file_name.lower().endswith(ext) for ext in VALID_EXTENSIONS):
                raise Exception("File format is invalid. Please upload a .mp4 or .mov file.")

            url = await self.storage.upload(video_data, file_name)

            video = VideoCreate(user_id=user_id, file_url=url, file_name=file_name)
            new_video = await self.video_repository.create(video)

            result = await asyncio.to_thread(self.model_inference.analyze_video, url)

            await self.analysis_result_repository.create(
                AnalysisResultCreate(
                    video_id=new_video.id,
                    task_id=result.task_id,
                    prediction="pending",
                    confidence=0.0
                )
            )

            return result
        except Exception as e:
            print(f"[analyze_video ERROR] {e}")
            raise


    async def get_result(self, task_id: str) -> ModelSchema:
        result = await asyncio.to_thread(self.model_inference.get_result, task_id)
        if result.status == "success" and result.result:
            existing = await self.analysis_result_repository.get_by_fields(task_id=task_id)
            if existing and existing.prediction == "pending":
                await self.analysis_result_repository.update(
                    obj_id=existing.id,
                    obj=AnalysisResultUpdate(
                        video_id=existing.video_id,
                        task_id=task_id,
                        prediction=result.result.prediction,
                        confidence=result.result.confidence
                    )
                )
        return result

async def get_model_use_case() -> AsyncGenerator[ModelUseCase, None]:
    yield ModelUseCaseImpl(s3_storage, video_repository, analysis_result_repository, model_inference)
