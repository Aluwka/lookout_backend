# src/usecases/analysis_result_usecase.py

from typing import List, Optional
from fastapi import Depends

from src.schemas.analysis_result_schema import (
    AnalysisResultCreate,
    AnalysisResultUpdate,
    AnalysisResultResponse,
    VideoAnalysisHistoryResponse
)
from src.repo.analysis_result_repo import analysis_result_repository, AnalysisResultRepository

class AnalysisResultUseCase:
    """
    Concrete use-case for analysis results: handles creation, retrieval, update, deletion,
    listing, and per-user history queries.
    """

    def __init__(self, repository: AnalysisResultRepository):
        self.repository = repository

    async def create_analysis_result(
        self, analysis_result: AnalysisResultCreate
    ) -> AnalysisResultResponse:
        return await self.repository.create(analysis_result)

    async def get_analysis_result(
        self, analysis_result_id: int
    ) -> Optional[AnalysisResultResponse]:
        return await self.repository.get(analysis_result_id)

    async def update_analysis_result(
        self, analysis_result_id: int, analysis_result: AnalysisResultUpdate
    ) -> AnalysisResultResponse:
        return await self.repository.update(analysis_result_id, analysis_result)

    async def delete_analysis_result(self, analysis_result_id: int) -> bool:
        return await self.repository.delete(analysis_result_id)

    async def list_analysis_results(
        self, page: int = 1, limit: int = 10
    ) -> List[AnalysisResultResponse]:
        offset = (page - 1) * limit
        return await self.repository.list(limit=limit, offset=offset)

    async def get_analysis_result_by_fields(
        self, **kwargs
    ) -> Optional[AnalysisResultResponse]:
        return await self.repository.get_by_fields(**kwargs)

    async def get_analysis_results_by_fields(
        self, **kwargs
    ) -> List[AnalysisResultResponse]:
        return await self.repository.get_all_by_fields(**kwargs)

    async def get_history_by_user(
        self, user_id: int
    ) -> List[VideoAnalysisHistoryResponse]:
        rows = await self.repository.get_history_for_user(user_id)
        # Each row is a sqlalchemy Row with named attributes
        return [
           VideoAnalysisHistoryResponse(
               file_name  = row.file_name,
               prediction = row.prediction,
               confidence = row.confidence,
               created_at = row.created_at   # ← correct
           )
            for row in rows
        ]

# Instantiate a singleton use-case
analysis_result_use_case = AnalysisResultUseCase(analysis_result_repository)

# Provider for FastAPI dependency injection
def get_analysis_result_use_case() -> AnalysisResultUseCase:
    return analysis_result_use_case
