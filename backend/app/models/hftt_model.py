"""
Simplified wrapper for HybridHFTT model inference.
This module provides a way to load and use the trained PyTorch model.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn


class PyTorchModelLoader:
    """Load PyTorch model checkpoint and provide inference interface."""
    
    def __init__(self, checkpoint_path: Path, icbhi_path: Path | None = None):
        """
        Initialize model loader.
        
        Args:
            checkpoint_path: Path to .pth checkpoint file
            icbhi_path: Path to ICBHI_2017 directory (for importing model architecture)
        """
        self.checkpoint_path = Path(checkpoint_path)
        self.icbhi_path = Path(icbhi_path) if icbhi_path else None
        self._checkpoint: dict[str, Any] | None = None
        self._model: nn.Module | None = None
        self._classifier: nn.Module | None = None
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load_checkpoint(self) -> dict[str, Any]:
        """Load checkpoint from file."""
        if self._checkpoint is None:
            if not self.checkpoint_path.exists():
                raise FileNotFoundError(f"Checkpoint not found: {self.checkpoint_path}")
            
            self._checkpoint = torch.load(
                str(self.checkpoint_path),
                map_location=self._device,
                weights_only=False
            )
        return self._checkpoint
    
    def get_model_info(self) -> dict[str, Any]:
        """Get model information from checkpoint."""
        checkpoint = self.load_checkpoint()
        
        info = {
            "epoch": checkpoint.get("epoch", None),
            "has_model": "model" in checkpoint,
            "has_classifier": "classifier" in checkpoint,
            "has_projector": "projector" in checkpoint,
        }
        
        # Get args info if available
        if "args" in checkpoint:
            args = checkpoint["args"]
            info.update({
                "model_type": getattr(args, "model", "unknown"),
                "n_cls": getattr(args, "n_cls", None),
                "n_mels": getattr(args, "n_mels", None),
                "sample_rate": getattr(args, "sample_rate", None),
                "desired_length": getattr(args, "desired_length", None),
            })
        
        # Get classifier info
        if "classifier" in checkpoint:
            classifier_state = checkpoint["classifier"]
            if isinstance(classifier_state, list):
                classifier_state = classifier_state[0]
            
            if "weight" in classifier_state:
                info["classifier_input_dim"] = classifier_state["weight"].shape[1]
                info["classifier_output_dim"] = classifier_state["weight"].shape[0]
        
        return info


def create_simple_classifier(input_dim: int, output_dim: int) -> nn.Module:
    """Create a simple classifier for inference."""
    return nn.Linear(input_dim, output_dim)


def load_model_with_wrapper(
    checkpoint_path: Path,
    icbhi_path: Path | None = None,
    use_icbhi_import: bool = True,
) -> tuple[nn.Module, nn.Module]:
    """
    Load model and classifier from checkpoint.
    
    This function attempts to load the full model architecture from ICBHI_2017.
    If that's not possible, it provides a minimal wrapper.
    
    Args:
        checkpoint_path: Path to .pth checkpoint
        icbhi_path: Path to ICBHI_2017 directory
        use_icbhi_import: Whether to try importing from ICBHI_2017
    
    Returns:
        Tuple of (model, classifier)
    """
    checkpoint = torch.load(str(checkpoint_path), map_location="cpu", weights_only=False)
    
    # Get model info
    args = checkpoint.get("args", None)
    model_type = getattr(args, "model", None) if args else None
    
    if use_icbhi_import and icbhi_path and Path(icbhi_path).exists():
        # Try to import from ICBHI_2017
        icbhi_path_str = str(Path(icbhi_path).absolute())
        if icbhi_path_str not in sys.path:
            sys.path.insert(0, icbhi_path_str)
        
        try:
            # Change to ICBHI directory temporarily to handle relative imports
            import os
            original_cwd = os.getcwd()
            
            try:
                os.chdir(icbhi_path_str)
                from models import get_backbone_class
                
                # Create model with same architecture as training
                if model_type == "hftt":
                    if hasattr(args, "nospec") and args.nospec:
                        kwargs = {"spec_transform": None}
                    else:
                        # Create SpecAugment if needed
                        try:
                            from util.augmentation import SpecAugment
                            kwargs = {"spec_transform": SpecAugment(args)}
                        except ImportError:
                            kwargs = {"spec_transform": None}
                    
                    # BEATs model path - use absolute path
                    beats_model_path = Path(icbhi_path_str) / "pretrained_models" / "BEATs_iter3_plus_AS2M.pt"
                    if beats_model_path.exists():
                        kwargs["beats_model_path"] = str(beats_model_path)
                    
                    model_class = get_backbone_class("hftt")
                    model = model_class(**kwargs)
                    
                elif model_type == "beats":
                    if hasattr(args, "nospec") and args.nospec:
                        kwargs = {"spec_transform": None}
                    else:
                        try:
                            from util.augmentation import SpecAugment
                            kwargs = {"spec_transform": SpecAugment(args)}
                        except ImportError:
                            kwargs = {"spec_transform": None}
                    
                    # BEATs model path - use absolute path
                    beats_model_path = Path(icbhi_path_str) / "pretrained_models" / "BEATs_iter3_plus_AS2M.pt"
                    if beats_model_path.exists():
                        kwargs["model_path"] = str(beats_model_path)
                    
                    model_class = get_backbone_class("beats")
                    model = model_class(**kwargs)
                else:
                    raise ValueError(f"Unsupported model type: {model_type}")
                
                model.load_state_dict(checkpoint["model"])
                model.eval()
                
                # Create classifier
                classifier = create_simple_classifier(
                    input_dim=model.final_feat_dim,
                    output_dim=args.n_cls if args else 4
                )
                classifier_state = checkpoint["classifier"]
                if isinstance(classifier_state, list):
                    classifier_state = classifier_state[0]
                classifier.load_state_dict(classifier_state)
                classifier.eval()
                
                return model, classifier
            finally:
                os.chdir(original_cwd)
            
        except Exception as e:
            import traceback
            error_msg = f"Could not import from ICBHI_2017: {e}\n{traceback.format_exc()}"
            print(f"Warning: {error_msg}")
            # Don't remove path yet, might be needed for debugging
            raise RuntimeError(
                f"Failed to load PyTorch model from {checkpoint_path}: {error_msg}\n"
                f"Make sure ICBHI_2017 directory is accessible at {icbhi_path}"
            ) from e
    
    # Fallback: minimal wrapper (may not work correctly)
    # This is a placeholder - user should ensure ICBHI_2017 is available
    raise RuntimeError(
        "Cannot load model without ICBHI_2017 architecture. "
        "Please ensure ICBHI_2017 directory is accessible or provide icbhi_path."
    )

