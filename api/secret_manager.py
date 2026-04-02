import os
from pathlib import Path


class SecretManagerError(RuntimeError):
    """Raised when a required secret cannot be resolved."""


def _read_secret_file(path_value: str) -> str:
    p = Path(path_value)
    if not p.exists() or not p.is_file():
        raise SecretManagerError(f"JWT secret file not found: {p}")
    secret = p.read_text(encoding="utf-8").strip()
    if not secret:
        raise SecretManagerError(f"JWT secret file is empty: {p}")
    return secret


def get_jwt_secret() -> str:
    """
    Resolve JWT signing secret with explicit precedence.

    Precedence:
      1) JWT_SECRET
      2) JWT_SECRET_FILE (file content)
      3) DEV_ALLOW_INSECURE_JWT=true => insecure fallback for local development only
    """
    env_secret = os.getenv("JWT_SECRET", "").strip()
    if env_secret:
        return env_secret

    env_secret_file = os.getenv("JWT_SECRET_FILE", "").strip()
    if env_secret_file:
        return _read_secret_file(env_secret_file)

    if os.getenv("DEV_ALLOW_INSECURE_JWT", "false").lower() == "true":
        return "dev-insecure-secret-change-me"

    raise SecretManagerError(
        "Missing JWT secret. Set JWT_SECRET or JWT_SECRET_FILE. "
        "For local dev only, set DEV_ALLOW_INSECURE_JWT=true."
    )


def get_admin_api_key() -> str:
    """Resolve admin bootstrap API key used to mint JWT access tokens."""
    key = os.getenv("API_ADMIN_KEY", "").strip()
    if not key:
        raise SecretManagerError("Missing API_ADMIN_KEY secret.")
    return key
