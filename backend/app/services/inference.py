from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort

from ..core.config import settings
from ..models.prediction import Label


def get_inference_service():
    """Get the appropriate inference service based on model_type config."""
    if settings.model_type.lower() == "pytorch":
        from .pytorch_inference import get_pytorch_inference_service
        return get_pytorch_inference_service()
    else:
        # Default to ONNX
        return inference_service


class AudioInferenceService:
    """Run ONNX model inference on lung sound audio clips."""

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or settings.model_path
        self._session: ort.InferenceSession | None = None
        self._lock = asyncio.Lock()

    async def load(self) -> None:
        async with self._lock:
            if self._session is None:
                providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
                self._session = ort.InferenceSession(
                    str(self.model_path),
                    providers=providers,
                )

    async def predict(self, features: np.ndarray) -> dict[str, Any]:
        if self._session is None:
            await self.load()
        assert self._session is not None

        batched = np.expand_dims(features, axis=(0, 1)).astype(np.float32)
        inputs = {self._session.get_inputs()[0].name: batched}
        outputs = self._session.run(None, inputs)
        logits = outputs[0].squeeze()
        probabilities = self._softmax(logits)

        label_idx = int(probabilities.argmax())
        label = list(Label)[label_idx]

        return {
            "label": label,
            "confidence": float(probabilities[label_idx]),
            "probabilities": {
                label.value: float(probabilities[idx])
                for idx, label in enumerate(Label)
            },
        }

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        exp = np.exp(logits - np.max(logits))
        return exp / exp.sum(axis=-1, keepdims=True)


inference_service = AudioInferenceService()


# For backward compatibility, export the service getter
__all__ = ["AudioInferenceService", "inference_service", "get_inference_service"]

