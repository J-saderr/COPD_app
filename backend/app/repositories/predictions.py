from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import ReturnDocument

from ..core.config import settings
from ..models.prediction import Label, Prediction, PredictionCreate, PredictionStatus


class PredictionRepository:
    """MongoDB repository for prediction metadata."""

    def __init__(self, client: AsyncIOMotorClient) -> None:
        self._client = client

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return self._client[settings.mongo_db]["predictions"]

    async def create(self, payload: PredictionCreate) -> Prediction:
        document = payload.model_dump()
        document.update(
            {
                "status": PredictionStatus.PENDING.value,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        result = await self.collection.insert_one(document)
        document["_id"] = str(result.inserted_id)
        return Prediction(**document)

    async def get(self, prediction_id: str) -> Optional[Prediction]:
        try:
            oid = ObjectId(prediction_id)
        except InvalidId:
            return None

        document = await self.collection.find_one({"_id": oid})
        if not document:
            return None
        return Prediction(**self._normalize(document))

    async def list_recent(self, limit: int = 20) -> list[Prediction]:
        cursor = self.collection.find().sort("created_at", -1).limit(limit)
        return [Prediction(**self._normalize(doc)) async for doc in cursor]

    async def update_status(
        self,
        prediction_id: str,
        status: PredictionStatus,
        *,
        label: Optional[Label] = None,
        confidence: Optional[float] = None,
        probabilities: Optional[dict[str, float]] = None,
        notes: Optional[str] = None,
    ) -> Optional[Prediction]:
        updates: dict[str, Any] = {
            "status": status.value,
            "updated_at": datetime.utcnow(),
        }
        if label is not None:
            updates["label"] = label.value
        if confidence is not None:
            updates["confidence"] = confidence
        if probabilities is not None:
            updates["probabilities"] = probabilities
        if notes is not None:
            updates["notes"] = notes

        document = await self.collection.find_one_and_update(
            {"_id": ObjectId(prediction_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        if not document:
            return None
        return Prediction(**self._normalize(document))

    @staticmethod
    def _normalize(document: dict[str, Any]) -> dict[str, Any]:
        document["_id"] = str(document["_id"])
        return document

