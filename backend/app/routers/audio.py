from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from motor.motor_asyncio import AsyncIOMotorClient

from ..core.config import settings
from ..models.prediction import Prediction, PredictionCreate, PredictionStatus
from ..repositories.predictions import PredictionRepository
from ..services.inference import get_inference_service
from ..services.storage import storage_service
from ..utils.audio import extract_mel_spectrogram, load_waveform

router = APIRouter()

_mongo_client = AsyncIOMotorClient(settings.mongo_uri)
_repository = PredictionRepository(_mongo_client)


def get_repository() -> PredictionRepository:
    return _repository


@router.post(
    "",
    response_model=Prediction,
    status_code=201,
    summary="Upload lung sound audio for analysis",
)
async def upload_audio(
    repository: Annotated[PredictionRepository, Depends(get_repository)],
    file: Annotated[UploadFile, File(...)],
) -> Prediction:
    if not file.content_type or not file.content_type.startswith("audio"):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    saved_path = await storage_service.save_upload(file)
    prediction = await repository.create(
        PredictionCreate(
            filename=file.filename or Path(saved_path).name,
            content_type=file.content_type,
            file_size=saved_path.stat().st_size,
            storage_path=str(saved_path),
        )
    )

    asyncio.create_task(_process_prediction(repository, prediction.id, saved_path))
    return prediction


@router.get(
    "/{prediction_id}",
    response_model=Prediction,
    summary="Retrieve prediction by identifier",
)
async def get_prediction(
    repository: Annotated[PredictionRepository, Depends(get_repository)],
    prediction_id: str,
) -> Prediction:
    prediction = await repository.get(prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction


@router.get(
    "",
    response_model=list[Prediction],
    summary="List recent predictions",
    response_description="List of recent predictions ordered by creation time",
)
async def list_predictions(
    repository: Annotated[PredictionRepository, Depends(get_repository)],
    limit: int = 20,
) -> list[Prediction]:
    return await repository.list_recent(limit=limit)


async def _process_prediction(
    repository: PredictionRepository,
    prediction_id: str,
    audio_path: Path,
) -> None:
    try:
        # Get the appropriate inference service based on config
        inference_service = get_inference_service()
        
        # Load waveform
        waveform = load_waveform(audio_path)
        
        # Different models expect different inputs:
        # - ONNX: mel-spectrogram features
        # - PyTorch: raw waveform
        if settings.model_type.lower() == "pytorch":
            # PyTorch model expects raw waveform
            result = await inference_service.predict(waveform)
        else:
            # ONNX model expects mel-spectrogram
            features = extract_mel_spectrogram(waveform)
            result = await inference_service.predict(features)

        await repository.update_status(
            prediction_id,
            PredictionStatus.COMPLETED,
            label=result["label"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
        )
    except Exception as exc:  # noqa: BLE001
        await repository.update_status(
            prediction_id,
            PredictionStatus.FAILED,
            notes=str(exc),
        )
    finally:
        # Keep the audio file for traceability; uncomment to delete after processing.
        # await storage_service.delete_file(audio_path)
        await asyncio.sleep(0)

