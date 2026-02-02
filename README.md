## Backend: COPD Lung Sound Inference API

### Prerequisites
- Python 3.11+
- MongoDB instance (local `mongodb://localhost:27017`)
- Pretrained ONNX model at `models/audio_classifier.onnx` (configure via `MODEL_PATH`)

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```
### Run development server
#### BE
```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
#### FE
```bash
cd ../COPD_app/frontend
npm run dev
```
### Open website in site http://localhost:3000
