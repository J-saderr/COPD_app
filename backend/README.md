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

### Environment
Create `.env` in `backend/` (FastAPI auto-loads from project root):
```
MONGO_URI=mongodb://localhost:27017/copd_app
MONGO_DB=copd_app
UPLOAD_DIR=/tmp/copd/uploads
MODEL_PATH=models/audio_classifier.onnx
ALLOW_ORIGINS=http://localhost:3000
```

> ⚠️ If your environment provides the `workflow` library with `ConfigManager`, place sensitive and runtime settings in `/app/infra/infra.json` and `/app/resources/momo.json` respectively. The API will read from those paths when available.

### Run development server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Overview
- `POST /api/audio/` — Upload audio file, starts asynchronous inference.
- `GET /api/audio/{prediction_id}` — Fetch prediction status & result.
- `GET /api/audio/` — List recent predictions.
- `GET /healthz` — Basic health check.

### Project Structure
```
backend/
  app/
    core/         # config & settings
    models/       # pydantic view models
    repositories/ # MongoDB access layer
    routers/      # FastAPI routers
    services/     # storage & inference services
    utils/        # audio preprocessing helpers
  requirements.txt
  README.md
```

### Next Steps
- Integrate authentication middleware.
- Move background inference to a Celery/RQ worker.
- Add unit tests & contract tests for endpoints.
- Plug in real ONNX/TorchScript model and validation logic.


