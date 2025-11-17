# PyTorch Model Setup Guide

Hướng dẫn sử dụng PyTorch model (.pth) cho COPD Lung Sound Inference API.

## Yêu cầu

1. **PyTorch model checkpoint**: File `.pth` từ ICBHI_2017 training
2. **ICBHI_2017 directory**: Thư mục chứa model architecture (HybridHFTT/BEATs)
3. **Dependencies**: Đã cài đặt trong `requirements.txt`

## Cấu hình

### 1. Environment Variables

Tạo file `.env` trong thư mục `backend/` hoặc set environment variables:

```bash
# Model configuration
MODEL_TYPE=pytorch  # hoặc "onnx" cho ONNX model
MODEL_PATH=/Users/vothao/ICBHI_2017/scripts/best.pth
ICBHI_PATH=/Users/vothao/ICBHI_2017

# Hoặc dùng relative path
MODEL_PATH=../ICBHI_2017/scripts/best.pth
ICBHI_PATH=../ICBHI_2017
```

### 2. Config trong code

Nếu không dùng `.env`, có thể set trong config:

```python
# backend/app/core/config.py (đã được cập nhật)
model_type: str = "pytorch"
model_path: Path = Path("/Users/vothao/ICBHI_2017/scripts/best.pth")
icbhi_path: Optional[Path] = Path("/Users/vothao/ICBHI_2017")
```

## Model Architecture

Model được sử dụng:
- **HybridHFTT**: Hybrid Feature Transformer với BEATs encoder
- **Input**: Raw audio waveform (80000 samples = 16000 Hz * 5 seconds)
- **Output**: 4 classes: `["normal", "crackle", "wheeze", "both"]`

Model mapping:
- `normal` → `NONE`
- `crackle` → `CRACKLE`
- `wheeze` → `WHEEZE`
- `both` → `BOTH`

## Cài đặt

### 1. Cài đặt dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Kiểm tra model có load được không

```bash
python3 scripts/test_model_loading.py
```

Nếu thành công, bạn sẽ thấy:
```
✅ Model file found: /path/to/best.pth
✅ Checkpoint loaded successfully!
✅ Model structure validated!
✅ Test PASSED: Model can be loaded!
```

### 3. Chạy server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Sử dụng API

API endpoint giống như khi dùng ONNX model:

```bash
# Upload audio file
curl -X POST "http://localhost:8000/api/audio/" \
  -F "file=@path/to/audio.wav"

# Get prediction result
curl "http://localhost:8000/api/audio/{prediction_id}"
```

## Lưu ý

1. **Model path**: Đảm bảo `MODEL_PATH` trỏ đến file `.pth` hợp lệ
2. **ICBHI path**: `ICBHI_PATH` phải trỏ đến thư mục ICBHI_2017 chứa:
   - `model/hftt.py` hoặc `model/beats.py`
   - `BEATs/` directory
   - Các dependencies khác
3. **Memory**: PyTorch model có thể cần nhiều RAM hơn ONNX, đặc biệt với GPU
4. **Performance**: PyTorch model chậm hơn ONNX một chút do dynamic graph

## Troubleshooting

### Lỗi: "Cannot load model without ICBHI_2017 architecture"

**Giải pháp**: Đảm bảo `ICBHI_PATH` được set đúng và thư mục ICBHI_2017 có đầy đủ files.

### Lỗi: "Checkpoint not found"

**Giải pháp**: Kiểm tra `MODEL_PATH` có đúng không và file `.pth` có tồn tại.

### Lỗi: "Failed to import from ICBHI_2017"

**Giải pháp**: 
- Kiểm tra Python path
- Đảm bảo ICBHI_2017 có đầy đủ dependencies
- Thử set `use_icbhi_import=False` (không khuyến nghị)

## Chuyển đổi giữa ONNX và PyTorch

Để chuyển từ PyTorch sang ONNX:

```bash
# Set trong .env
MODEL_TYPE=onnx
MODEL_PATH=models/audio_classifier.onnx
```

Để chuyển từ ONNX sang PyTorch:

```bash
# Set trong .env
MODEL_TYPE=pytorch
MODEL_PATH=/path/to/best.pth
ICBHI_PATH=/path/to/ICBHI_2017
```

## Model Information

Để xem thông tin model:

```python
from app.services.pytorch_inference import get_pytorch_inference_service

service = get_pytorch_inference_service()
info = service.get_model_info()
print(info)
```

Output sẽ bao gồm:
- Model type (hftt/beats)
- Number of classes
- Sample rate
- Input dimensions
- Classifier dimensions


