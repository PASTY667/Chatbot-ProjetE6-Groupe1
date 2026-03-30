from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any

Role = Literal["admin", "user"]
Scope = Literal["company", "user_session"]

class JWTClaims(BaseModel):
    sub:str
    role: Role
    sid : str
    exp: int
    iat: int
    iss: Optional[str] = None
    aud: Optional[str] = None

class ErrorPayload(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class APIError(BaseModel):
    error: ErrorPayload

class IngestRequest(BaseModel):
    path_file: str = Field(..., description="Chemin du fichier à ingérer")
    collection_name: str | None = Field(default=None)
    doc_id: str | None = Field(default=None)

class IngestResponse(BaseModel):
    collection_name: str
    doc_id: str
    chunks_count: int
    inserted_id_count: int
    source_path: str

class SourceItem(BaseModel):
    scope: Scope
    collection_name: str
    doc_id: str
    score: float
    snippet: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

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