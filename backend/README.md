## Backend: COPD Lung Sound Inference API

### Prerequisites
- Python 3.11+
- MongoDB instance (local `mongodb://localhost:27017`)
- Pretrained model:
  - **ONNX model**: `models/audio_classifier.onnx` (configure via `MODEL_PATH`)
  - **PyTorch model**: `.pth` checkpoint from ICBHI_2017 training (see `PYTORCH_MODEL_SETUP.md`)

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Configuration

Create a `.env` file in `backend/` directory:

```bash
# Model configuration
MODEL_TYPE=onnx  # or "pytorch"
MODEL_PATH=models/audio_classifier.onnx  # For ONNX
# MODEL_PATH=/path/to/best.pth  # For PyTorch
# ICBHI_PATH=/path/to/ICBHI_2017  # Required for PyTorch model

# MongoDB
MONGO_URI=mongodb://localhost:27017/copd_app

# Other settings
UPLOAD_DIR=/tmp/copd/uploads
```

For PyTorch model setup, see [PYTORCH_MODEL_SETUP.md](PYTORCH_MODEL_SETUP.md).
### Run development server
#### BE
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
#### FE
```bash
cd ../COPD_app/frontend
npm run dev
```
### Open website in site http://localhost:3000