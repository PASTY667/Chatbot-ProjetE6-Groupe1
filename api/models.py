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

class IngestResponse(BaseModel):
    status: Literal["ok"] = "ok"
    scope: Scope
    collection_name: str
    doc_id: str
    chunks_count:int
    inserted_id: int
    source_path: str

class SourceItem(BaseModel):
    scope: Scope
    collection_name: str
    doc_id: str
    score: float
    snippet: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    use_company_docs: bool = True
    use_user_docs: bool = True
    k_company: int = Field(default=4, ge=0, le=20)
    k_user: int = Field(default=4, ge=0, le=20)

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem] = []