from __future__ import annotations

import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from ..core.config import settings


class AudioStorageService:
    """Persist audio files to local disk (placeholder for S3/MinIO)."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or settings.upload_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, upload: UploadFile) -> Path:
        suffix = Path(upload.filename or "").suffix or ".wav"
        dest_path = self.base_dir / f"{uuid.uuid4().hex}{suffix}"

        async with aiofiles.open(dest_path, "wb") as f:
            while chunk := await upload.read(1024 * 1024):
                await f.write(chunk)

        await upload.close()
        return dest_path

    async def delete_file(self, path: Path) -> None:
        if path.exists():
            path.unlink()


storage_service = AudioStorageService()


