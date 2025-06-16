from datetime import datetime
from pydantic import BaseModel, Field
from .mixins.id_mixin import IDMixin
from typing import Optional
from .mixins.time_mixin import CreatedAtMixin


class AnalysisResultBase(BaseModel):
    """
    Base schema for analysis result.
    """
    video_id: int = Field(..., description="ID of the video associated with the analysis result")
    task_id: str = Field(..., description="ID of the task associated with the analysis result")
    prediction: str = Field(..., description="Prediction result of the analysis")
    confidence: float = Field(..., description="Confidence level of the prediction")

class AnalysisResultCreate(AnalysisResultBase):
    """
    Schema for creating a new analysis result entry.
    """
    pass

class AnalysisResultUpdate(AnalysisResultBase):
    """
    Schema for updating an existing analysis result entry.
    """
    pass


class AnalysisResultResponse(AnalysisResultBase, IDMixin, CreatedAtMixin):
    """
    Schema for responding with analysis result entry details.
    """
    pass

class VideoAnalysisHistoryResponse(BaseModel):
    """
    Joined video + analysis_result for profile history.
    """
    file_name: Optional[str]  = Field(None, description="Original file name")
    prediction: str           = Field(..., description="REAL or FAKE")
    confidence: float         = Field(..., description="0.0–1.0")
    created_at:  datetime     = Field(..., description="When analysis finished")

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }
