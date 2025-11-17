"""
PyTorch model inference service for HF-TT model.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from ..core.config import settings
from ..models.prediction import Label
from ..models.hftt_model import load_model_with_wrapper, PyTorchModelLoader


class PyTorchAudioInferenceService:
    """Run PyTorch model inference on lung sound audio clips."""

    def __init__(
        self,
        model_path: Path | None = None,
        icbhi_path: Path | None = None,
    ) -> None:
        self.model_path = model_path or settings.model_path
        self.icbhi_path = icbhi_path or settings.icbhi_path
        self._model: nn.Module | None = None
        self._classifier: nn.Module | None = None
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._lock = asyncio.Lock()
        self._model_info: dict[str, Any] | None = None

    async def load(self) -> None:
        """Load PyTorch model and classifier from checkpoint."""
        async with self._lock:
            if self._model is None:
                try:
                    # Load model info first
                    loader = PyTorchModelLoader(self.model_path, self.icbhi_path)
                    self._model_info = loader.get_model_info()
                    
                    # Load model and classifier
                    self._model, self._classifier = load_model_with_wrapper(
                        checkpoint_path=self.model_path,
                        icbhi_path=self.icbhi_path,
                        use_icbhi_import=True,
                    )
                    
                    # Move to device
                    self._model.to(self._device)
                    self._classifier.to(self._device)
                    
                    # Set to eval mode
                    self._model.eval()
                    self._classifier.eval()
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    raise RuntimeError(
                        f"Failed to load PyTorch model from {self.model_path}:\n"
                        f"Error: {str(e)}\n"
                        f"Traceback:\n{error_details}\n"
                        f"Make sure:\n"
                        f"  1. ICBHI_2017 directory is accessible at {self.icbhi_path}\n"
                        f"  2. Model path is correct: {self.model_path}\n"
                        f"  3. Required dependencies are installed"
                    ) from e

    async def predict(self, waveform: np.ndarray) -> dict[str, Any]:
        """
        Predict lung sound class from raw audio waveform.
        
        Args:
            waveform: Raw audio waveform array of shape (T,) where T = sample_rate * duration
        
        Returns:
            Dictionary with label, confidence, and probabilities
        """
        if self._model is None:
            await self.load()
        assert self._model is not None
        assert self._classifier is not None

        # Convert numpy array to torch tensor
        if isinstance(waveform, np.ndarray):
            waveform_tensor = torch.from_numpy(waveform).float()
        else:
            waveform_tensor = torch.tensor(waveform, dtype=torch.float32)
        
        # Add batch dimension: [T] -> [1, T]
        waveform_tensor = waveform_tensor.unsqueeze(0)
        waveform_tensor = waveform_tensor.to(self._device)

        # Run inference (no gradient calculation)
        with torch.no_grad():
            # Model forward pass
            # For HFTT/BEATs models, input is raw waveform
            features = self._model(waveform_tensor, training=False)
            
            # Features shape: [B, 1, D] or [B, N, D]
            # Classifier expects [B, D] or [B, N, D]
            if features.dim() == 3 and features.size(1) == 1:
                # [B, 1, D] -> [B, D]
                features = features.squeeze(1)
            elif features.dim() == 3:
                # [B, N, D] -> mean over temporal dimension -> [B, D]
                features = features.mean(dim=1)
            
            # Classifier forward pass
            logits = self._classifier(features)
        
        # Convert to numpy
        logits = logits.cpu().numpy().squeeze()
        probabilities = self._softmax(logits)

        # Get predicted label
        label_idx = int(probabilities.argmax())
        
        # Map to Label enum
        # Model classes: ["normal", "crackle", "wheeze", "both"]
        # Label enum: CRACKLE, WHEEZE, BOTH, NONE
        label_mapping = {
            0: Label.NONE,      # normal -> NONE
            1: Label.CRACKLE,   # crackle -> CRACKLE
            2: Label.WHEEZE,    # wheeze -> WHEEZE
            3: Label.BOTH,      # both -> BOTH
        }
        label = label_mapping.get(label_idx, Label.NONE)

        # Create probability dictionary
        prob_dict = {}
        for idx, label_enum in enumerate(Label):
            # Map back from model index to Label enum
            # Need to find which model index corresponds to which label
            for model_idx, mapped_label in label_mapping.items():
                if mapped_label == label_enum:
                    prob_dict[label_enum.value] = float(probabilities[model_idx])
                    break
            else:
                prob_dict[label_enum.value] = 0.0

        return {
            "label": label,
            "confidence": float(probabilities[label_idx]),
            "probabilities": prob_dict,
        }

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        """Compute softmax probabilities."""
        exp = np.exp(logits - np.max(logits))
        return exp / exp.sum(axis=-1, keepdims=True)

    def get_model_info(self) -> dict[str, Any]:
        """Get model information."""
        if self._model_info is None:
            loader = PyTorchModelLoader(self.model_path, self.icbhi_path)
            self._model_info = loader.get_model_info()
        return self._model_info


# Global instance (will be initialized based on config)
pytorch_inference_service: PyTorchAudioInferenceService | None = None


def get_pytorch_inference_service() -> PyTorchAudioInferenceService:
    """Get or create PyTorch inference service instance."""
    global pytorch_inference_service
    if pytorch_inference_service is None:
        pytorch_inference_service = PyTorchAudioInferenceService()
    return pytorch_inference_service

