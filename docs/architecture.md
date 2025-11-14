## COPD Lung Sound Detection Web Platform

### Overview
- **Goal**: Provide a secure web experience where clinicians and patients can upload lung-sound audio, receive AI predictions (`crackle`, `wheeze`, `both`, `none`) with confidence scores, and manage results over time.
- **Architecture Style**: Modular web app with a decoupled React frontend, Python backend services, and MongoDB for persistence. Audio processing runs in a dedicated inference service to keep UI responsive.

### Technology Choices
- **Frontend**: Next.js 14 (React) with TypeScript for SEO, routing, and server-actions support. Alternative: Vite + React if pure SPA is preferred.
- **Backend**: FastAPI + Uvicorn for async Python APIs, Pydantic models, and easy ML model serving. Alternatives considered: Django REST (heavier), Flask (minimal tooling).
- **Model Serving**: Dedicated inference module using the existing trained model (TorchScript/ONNX). Supports GPU when available; otherwise CPU with batched processing.
- **Database**: MongoDB for flexible storage of prediction metadata, audio processing status, and user feedback. Alternative: PostgreSQL if relational reporting becomes critical.
- **Object Storage**: MinIO/S3-compatible bucket for raw audio and derived spectrograms. MongoDB keeps references to blob locations.
- **Authentication**: OAuth2 (Keycloak/Auth0) or custom JWT with FastAPI's security utilities.
- **CI/CD**: GitLab CI pipelines with lint/test/build steps, Docker images pushed to registry.

### High-Level Components
1. **`frontend/` (Next.js)**  
   - Pages: Upload dashboard, history, admin analytics.  
   - Components: Audio recorder, wave/spectrogram viewer, result cards, feedback form.  
   - Clients: REST client for backend, WebSocket for live inference progress.

2. **`backend/app/` (FastAPI)**  
   - `routers/audio.py`: Endpoints for upload, status, history, feedback.  
   - `services/inference.py`: Loads trained model, runs predictions, publishes events.  
   - `services/storage.py`: Handles S3 uploads/downloads and local temp files.  
   - `repositories/predictions.py`: CRUD with MongoDB.  
   - `core/config.py`: Centralizes settings via environment variables (leverages `workflow` ConfigManager if available).

3. **Task Queue (Optional)**  
   - Celery/RQ + Redis for long-running inference jobs.  
   - Allows retry, rate limiting, and background processing.

4. **Monitoring & Observability**  
   - Prometheus metrics, structured logging (JSON), tracing with OpenTelemetry.  
   - Error tracking via Sentry.

### Data Flow
1. User uploads audio → frontend streams to backend `/api/audio` via multipart.  
2. Backend stores raw file in object storage, creates MongoDB record (`pending`).  
3. Inference service processes audio, generates prediction, updates MongoDB (`completed`) with probabilities and metadata.  
4. Frontend polls or listens via WebSocket for status → displays results and supporting visuals.  
5. User feedback (correct/incorrect) stored and optionally sent to labeling queue for retraining.

### Security Considerations
- Enforce HTTPS, rate limiting, and request size limits.  
- Validate audio format (sample rate, duration) before inference.  
- Encrypt stored audio and sensitive metadata.  
- Implement audit logs and consent management for medical data compliance.

### Deployment Topology (Suggestion)
- **Environment**: Dev / Staging / Prod.  
- **Containers**:  
  - `frontend` container served via CDN / reverse proxy.  
  - `backend-api` container exposing FastAPI via Gunicorn/Uvicorn workers.  
  - `inference-worker` container for queue consumers.  
  - MongoDB managed service or replica set.  
  - Object storage (MinIO/S3).  
- **Ingress**: Nginx/Traefik with TLS termination.  
- **Scaling**: Horizontal autoscaling based on CPU usage & queue length.

### Next Steps
- Scaffold `frontend/` Next.js app and set up upload UI.  
- Scaffold FastAPI backend with health, upload, prediction endpoints.  
- Integrate MongoDB client and configure environment management.  
- Wire frontend to backend, enable recording/upload workflows.  
- Add background processing, monitoring, and CI/CD automation.


