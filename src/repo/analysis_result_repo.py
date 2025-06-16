from contextlib import AbstractAsyncContextManager
from typing import Callable, List, TypeVar, Type

from sqlalchemy import select
from src.schemas.analysis_result_schema import AnalysisResultCreate, AnalysisResultUpdate, AnalysisResultResponse, VideoAnalysisHistoryResponse
from src.utils.model_adapter import model_to_schema
from src.models.video_model import VideoModel as Video
from src.models.analysis_result_model import AnalysisResultModel as AnalysisResult
from src.models.base_model import BaseModel
from src.usecases.repository import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.connections.database.postgres_connection import postgres


T = TypeVar("T", bound=BaseModel)

class AnalysisResultRepository(Repository):
    """Repository for analysis result operations."""

    def __init__(self, connection_pool: Callable[..., AbstractAsyncContextManager[AsyncSession]], model: Type[T]) -> None:
        self.connection_pool = connection_pool
        self.model = model

    async def create(self, obj: AnalysisResultCreate) -> AnalysisResultResponse:
        """Create a new analysis result."""
        async with self.connection_pool() as session:
            analysis_result = self.model(**obj.dict())
            session.add(analysis_result)
            await session.commit()
            await session.refresh(analysis_result)
            return model_to_schema(analysis_result, AnalysisResultResponse)
    
    async def get(self, obj_id: int) -> AnalysisResultResponse:
        """Retrieve an analysis result by ID."""
        async with self.connection_pool() as session:
            analysis_result = await session.get(self.model, obj_id)
            if analysis_result:
                return model_to_schema(analysis_result, AnalysisResultResponse)
            return None
        
    async def update(self, obj_id: int, obj: AnalysisResultUpdate) -> AnalysisResultResponse:
        """Update an existing analysis result."""
        async with self.connection_pool() as session:
            analysis_result = await session.get(self.model, obj_id)
            if analysis_result:
                for key, value in obj.dict(exclude_unset=True).items():
                    setattr(analysis_result, key, value)
                await session.commit()
                await session.refresh(analysis_result)
                return model_to_schema(analysis_result, AnalysisResultResponse)
            return None
    
    async def delete(self, obj_id: int) -> bool:
        """Delete an analysis result by ID."""
        async with self.connection_pool() as session:
            analysis_result = await session.get(self.model, obj_id)
            if analysis_result:
                await session.delete(analysis_result)
                await session.commit()
                return True
            return False
    
    async def list(self, limit: int, offset: int) -> List[AnalysisResultResponse]:
        """List analysis results with pagination."""
        async with self.connection_pool() as session:
            query = select(self.model).offset(offset).limit(limit)
            result = await session.execute(query)
            analysis_results = result.scalars().all()
            return [model_to_schema(analysis_result, AnalysisResultResponse) for analysis_result in analysis_results]
    
    async def get_by_fields(self, **kwargs) -> AnalysisResultResponse:
        """Retrieve an analysis result by specific fields."""
        async with self.connection_pool() as session:
            query = select(self.model).filter_by(**kwargs)
            result = await session.execute(query)
            analysis_result = result.scalars().first()
            if analysis_result:
                return model_to_schema(analysis_result, AnalysisResultResponse)
            return None
    
    async def get_all_by_fields(self, **kwargs) -> List[AnalysisResultResponse]:
        """Retrieve an analysis result by specific fields."""
        async with self.connection_pool() as session:
            query = select(self.model).filter_by(**kwargs)
            result = await session.execute(query)
            analysis_results = result.scalars().all()
            return [model_to_schema(analysis_result, AnalysisResultResponse) for analysis_result in analysis_results]
        
    async def get_history_for_user(self, user_id: int):
        async with self.connection_pool() as session:
            query = (
                select(
                    Video.file_name,
                    AnalysisResult.prediction,
                    AnalysisResult.confidence,
                    AnalysisResult.created_at
                )
                .join(AnalysisResult, AnalysisResult.video_id == Video.id)
                .where(Video.user_id == user_id)
                .order_by(AnalysisResult.created_at.desc())
            )
            result = await session.execute(query)
            # returns List[Row(file_name=..., prediction=..., etc.)]
            return result.all()
        

analysis_result_repository = AnalysisResultRepository(postgres.connection_pool_factory(), AnalysisResult)