from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from workflow import ConfigManager

    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False

DEFAULT_INFRA_PATH = Path("/app/infra/infra.json")
DEFAULT_MOMO_PATH = Path("/app/resources/momo.json")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        protected_namespaces=("settings_",),
    )

    app_name: str = "COPD Lung Sound Inference API"
    environment: str = Field(default="development")
    mongo_uri: str = Field(default="mongodb://localhost:27017/copd_app")
    mongo_db: str = Field(default="copd_app")
    storage_bucket: str = Field(default="lung-audio")
    upload_dir: Path = Field(default=Path("/tmp/copd/uploads"))
    model_path: Path = Field(default=Path("models/audio_classifier.onnx"))
    inference_batch_size: int = Field(default=1)
    allow_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    infra_path: Optional[Path] = DEFAULT_INFRA_PATH
    momo_path: Optional[Path] = DEFAULT_MOMO_PATH

def _load_workflow_config() -> Dict[str, Any]:
    """Attempt to load configuration using workflow ConfigManager if available."""
    if not WORKFLOW_AVAILABLE:
        return {}

    infra_path = DEFAULT_INFRA_PATH
    momo_path = DEFAULT_MOMO_PATH

    if not infra_path.exists() or not momo_path.exists():
        return {}

    config = ConfigManager.load(
        infra_path=str(infra_path),
        momo_path=str(momo_path),
    )
    # ConfigManager returns nested structure; convert to dict
    merged: Dict[str, Any] = json.loads(config.to_json())
    return merged.get("backend", merged)


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    workflow_config = _load_workflow_config()
    if workflow_config:
        return Settings(**workflow_config)
    return Settings()


settings = get_settings()

