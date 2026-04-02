import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.models import TokenRequest, TokenResponse
from api.secret_manager import SecretManagerError, get_admin_api_key, get_jwt_secret

ALGORITHM = "HS256"
DEFAULT_TTL_SECONDS = int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


def create_access_token(subject: str, expires_seconds: int = DEFAULT_TTL_SECONDS, extra_claims: dict | None = None) -> str:
    secret = get_jwt_secret()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_seconds)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    header = {"alg": ALGORITHM, "typ": "JWT"}
    return _encode_jwt(header, payload, secret)


def decode_access_token(token: str) -> dict:
    secret = get_jwt_secret()
    return _decode_jwt(token, secret)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(raw: str) -> bytes:
    padding = "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def _encode_jwt(header: dict, payload: dict, secret: str) -> str:
    header_part = _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signing_input = f"{header_part}.{payload_part}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_part = _b64url_encode(signature)
    return f"{header_part}.{payload_part}.{signature_part}"


def _decode_jwt(token: str, secret: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Malformed token")

    header_part, payload_part, signature_part = parts
    signing_input = f"{header_part}.{payload_part}".encode("ascii")
    expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    given_sig = _b64url_decode(signature_part)
    if not hmac.compare_digest(expected_sig, given_sig):
        raise ValueError("Invalid signature")

    header = json.loads(_b64url_decode(header_part).decode("utf-8"))
    if header.get("alg") != ALGORITHM:
        raise ValueError("Unsupported JWT algorithm")

    payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
    now = int(datetime.now(timezone.utc).timestamp())
    if int(payload.get("exp", 0)) < now:
        raise ValueError("Token expired")

    return payload


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    try:
        payload = decode_access_token(credentials.credentials)
        if "sub" not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return payload
    except ValueError as exc:
        message = "Token expired" if str(exc) == "Token expired" else "Invalid token"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
    except SecretManagerError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.post("/token", response_model=TokenResponse)
def issue_token(payload: TokenRequest):
    admin_key = get_admin_api_key()
    if payload.api_key != admin_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(payload.subject)
    return TokenResponse(access_token=token, expires_in=DEFAULT_TTL_SECONDS)
