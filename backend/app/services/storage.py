import os
from pathlib import Path
from typing import Optional
from app.core.config import settings

# Base local directory for file storage
LOCAL_STORAGE_DIR = Path("data/storage")


def save_file(storage_path: str, content: bytes) -> str:
    """Save raw file bytes into private storage."""
    target_path = LOCAL_STORAGE_DIR / storage_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(content)
    return storage_path


def read_file(storage_path: str) -> Optional[bytes]:
    """Read file content from storage."""
    target_path = LOCAL_STORAGE_DIR / storage_path
    if not target_path.exists():
        return None
    return target_path.read_bytes()


def delete_file(storage_path: str) -> bool:
    """Delete a file from storage."""
    target_path = LOCAL_STORAGE_DIR / storage_path
    if target_path.exists():
        try:
            target_path.unlink()
            return True
        except OSError:
            return False
    return False
