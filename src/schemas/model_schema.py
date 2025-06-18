from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, Any

T = TypeVar("Schemas", bound=Any)

class ModelSchema(BaseModel, Generic[T]):
    status: str = Field(..., description="Status of the model")
    result: Optional[T] = Field(None, description="Result of the model analysis")
    task_id: Optional[str] = Field(None, description="Task ID for tracking the analysis")

class ModelResultSchema(BaseModel):
    prediction: str = Field(..., description="Prediction result (FAKE or REAL)")
    confidence: float = Field(..., description="Confidence percentage (e.g. 94.7)")
    probability: str = Field(..., description="Raw model output (e.g. 0.1342)")
    comment: str = Field(..., description="Explanation of the result")
    heatmap_path: Optional[str] = None
    extreme_path: Optional[str] = None
    gallery_path: Optional[str] = None

