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


class IngestRequest(BaseModel):
    path_file: str = Field(..., description="Absolute or relative path to file")
    collection_name: str | None = None
    doc_id: str | None = None


class IngestResponse(BaseModel):
    collection_name: str
    doc_id: str
    chunks_count: int
    inserted_id_count: int
    source_path: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    k: int = Field(default=5, ge=1, le=20)
    use_official: bool = True
    include_user_collection: bool = True
    chat_id: str | None = None
    user_collection_name: str | None = None
    collection_name: str | None = None


class ChatResponse(BaseModel):
    answer: str
    contexts: list[str]
    metadatas: list[dict[str, Any]]
    sources_used: list[str] = []
    warnings: list[str] = []


class HealthResponse(BaseModel):
    status: str
    chroma_ok: bool
    ollama_ok: bool
    jwt_secret_ok: bool
