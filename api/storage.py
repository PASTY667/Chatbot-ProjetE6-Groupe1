import os
import re
from pathlib import Path

from fastapi import HTTPException, UploadFile


def _sanitize_segment(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "default"


def _storage_root() -> Path:
    root = Path(os.getenv("STORAGE_ROOT", "/data")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def build_target_dir(scope: str, chat_id: str | None) -> Path:
    scope_s = _sanitize_segment(scope)
    root = _storage_root()

    official_dirname = _sanitize_segment(os.getenv("OFFICIAL_SUBDIR", "official"))
    users_dirname = _sanitize_segment(os.getenv("USERS_SUBDIR", "users"))

    if scope_s == "official":
        target = root / official_dirname
        target.mkdir(parents=True, exist_ok=True)
        return target

    if scope_s != "user":
        raise HTTPException(status_code=400, detail="scope must be either 'user' or 'official'")

    if not chat_id:
        raise HTTPException(status_code=400, detail="chat_id is required for user scope")

    chat_dir = _sanitize_segment(chat_id)
    target = root / users_dirname / chat_dir
    target.mkdir(parents=True, exist_ok=True)
    return target


def save_uploaded_file(file: UploadFile, scope: str, chat_id: str | None) -> Path:
    filename = _sanitize_segment(Path(file.filename or "document").stem) + Path(file.filename or "document").suffix.lower()
    target_dir = build_target_dir(scope=scope, chat_id=chat_id)
    destination = target_dir / filename

    with destination.open("wb") as out:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    return destination


def resolve_collection_name(scope: str, chat_id: str | None, collection_name: str | None) -> str:
    if collection_name:
        return collection_name
    scope_s = _sanitize_segment(scope)
    if scope_s == "official":
        return "documents_official"
    chat = _sanitize_segment(chat_id or "default")
    return f"documents_user_{chat}"
