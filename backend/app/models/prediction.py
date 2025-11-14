from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Label(str, Enum):
    CRACKLE = "crackle"
    WHEEZE = "wheeze"
    BOTH = "both"
    NONE = "none"


class PredictionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PredictionCreate(BaseModel):
    filename: str
    content_type: str
    file_size: int
    storage_path: str
    user_id: Optional[str] = None


class Prediction(BaseModel):
    id: str = Field(alias="_id")
    filename: str
    content_type: str
    file_size: int
    storage_path: str
    status: PredictionStatus = PredictionStatus.PENDING
    label: Optional[Label] = None
    confidence: Optional[float] = None
    probabilities: Optional[dict[str, float]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda dt: dt.isoformat()},
    )

