from typing import Any
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str


class TokenRequest(BaseModel):
    api_key: str = Field(..., min_length=8)
    subject: str = Field(default="service-account")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# remplace IngestRequest + ChatRequest

class IngestRequest(BaseModel):
    path_file: str = Field(..., description="Absolute or relative path to file")
    target: str = Field(default="user", pattern="^(official|user)$")
    doc_id: str | None = None


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    k: int = Field(default=5, ge=1, le=20)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    collection_name: str | None = None
    k: int = Field(default=5, ge=1, le=20)


class ChatResponse(BaseModel):
    answer: str
    contexts: list[str]
    metadatas: list[dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    chroma_ok: bool
    ollama_ok: bool
    jwt_secret_ok: bool
