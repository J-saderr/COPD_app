#!/usr/bin/env python3
"""
Script to test if PyTorch model (.pth) can be loaded successfully.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import torch.nn as nn

# Path đến model
MODEL_PATH = Path("../ICBHI_2017/save/icbhi_hftt_projectors_loss_seed2_hftt/best.pth")

def test_model_loading():
    """Test loading the PyTorch model checkpoint."""
    
    # Kiểm tra file tồn tại
    if not MODEL_PATH.exists():
        print(f" ERROR: Model file not found at {MODEL_PATH}")
        return False
    
    print(f"[OK] Model file found: {MODEL_PATH}")
    print(f"   Size: {MODEL_PATH.stat().st_size / (1024**2):.2f} MB")
    
    # Load checkpoint
    try:
        print("\n[LOADING] Loading checkpoint...")
        checkpoint = torch.load(str(MODEL_PATH), map_location='cpu', weights_only=False)
        print("[OK] Checkpoint loaded successfully!")
        
        # Inspect checkpoint structure
        print("\n[INFO] Checkpoint keys:")
        for key in checkpoint.keys():
            if key == 'model':
                print(f"   - {key}: Model state_dict")
                if isinstance(checkpoint[key], dict):
                    print(f"     Model parameter count: {len(checkpoint[key])}")
                    # Show first few keys
                    sample_keys = list(checkpoint[key].keys())[:3]
                    print(f"     Sample keys: {sample_keys}")
            elif key == 'classifier':
                if isinstance(checkpoint[key], list):
                    print(f"   - {key}: List with {len(checkpoint[key])} items")
                    if len(checkpoint[key]) > 0:
                        print(f"     First item keys: {len(checkpoint[key][0])}")
                else:
                    print(f"   - {key}: Classifier state_dict")
                    print(f"     Classifier keys: {list(checkpoint[key].keys())}")
                    # Check shape
                    for k, v in checkpoint[key].items():
                        print(f"       {k}: shape {v.shape}")
            elif key == 'projector':
                print(f"   - {key}: Projector state_dict (not needed for inference)")
            elif key == 'args':
                args = checkpoint['args']
                print(f"   - {key}: Training arguments")
                if hasattr(args, 'n_cls'):
                    print(f"     n_cls: {args.n_cls}")
                if hasattr(args, 'cls_list'):
                    print(f"     cls_list: {args.cls_list}")
                if hasattr(args, 'model'):
                    print(f"     model: {args.model}")
                if hasattr(args, 'n_mels'):
                    print(f"     n_mels: {args.n_mels}")
                if hasattr(args, 'sample_rate'):
                    print(f"     sample_rate: {args.sample_rate}")
                if hasattr(args, 'desired_length'):
                    print(f"     desired_length: {args.desired_length}")
            else:
                print(f"   - {key}: {type(checkpoint[key])}")
        
        # Validate model structure
        print("\n[CHECK] Validating model structure...")
        
        if 'model' not in checkpoint:
            print("[ERROR] ERROR: 'model' key not found in checkpoint")
            return False
        
        if 'classifier' not in checkpoint:
            print("[ERROR] ERROR: 'classifier' key not found in checkpoint")
            return False
        
        model_state = checkpoint['model']
        classifier_state = checkpoint['classifier']
        
        # Handle classifier as list or dict
        if isinstance(classifier_state, list):
            classifier_state = classifier_state[0]
        
        # Check classifier shape
        if 'weight' in classifier_state:
            weight_shape = classifier_state['weight'].shape
            print(f"[OK] Classifier weight shape: {weight_shape}")
            print(f"   -> Input features: {weight_shape[1]}, Output classes: {weight_shape[0]}")
        
        print("\n[OK] Model structure validated!")
        print("\n[NOTE] Summary:")
        print(f"   - Model type: {checkpoint.get('args', type('Args', (), {'model': 'unknown'})).model if hasattr(checkpoint.get('args', type('Args', (), {})), 'model') else 'unknown'}")
        print(f"   - Number of classes: {checkpoint.get('args', type('Args', (), {'n_cls': 4})).n_cls if hasattr(checkpoint.get('args', type('Args', (), {})), 'n_cls') else 'unknown'}")
        print(f"   - Model can be loaded: [OK] YES")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] ERROR loading checkpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PyTorch Model Loading Test")
    print("=" * 60)
    
    success = test_model_loading()
    
    print("\n" + "=" * 60)
    if success:
        print("[OK] Test PASSED: Model can be loaded!")
    else:
        print("[ERROR] Test FAILED: Model cannot be loaded!")
    print("=" * 60)
    
    sys.exit(0 if success else 1)


