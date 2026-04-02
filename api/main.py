import logging as log
import os

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import utils.logger as logger
from api.auth import router as auth_router
from api.models import HealthResponse
from api.routesChat import router as chat_router
from api.routesIngest import router as ingest_router
from api.secret_manager import SecretManagerError, get_jwt_secret
from Vector.chroma_client import get_chroma_client

logger.get_logger()

app = FastAPI(title="RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    log.debug("Root endpoint called")
    return {"message": "Hello World"}


@app.get("/health", response_model=HealthResponse)
def health():
    log.info("Health check started")
    chroma_ok = True
    ollama_ok = True
    jwt_secret_ok = True

    try:
        _ = get_chroma_client()
    except Exception:
        log.exception("Chroma connectivity check failed")
        chroma_ok = False

    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        resp = httpx.get(f"{ollama_url}/api/tags", timeout=3)
        resp.raise_for_status()
    except Exception:
        log.exception("Ollama connectivity check failed")
        ollama_ok = False

    try:
        _ = get_jwt_secret()
    except SecretManagerError:
        log.exception("JWT secret retrieval failed")
        jwt_secret_ok = False

    status = "ok" if chroma_ok and ollama_ok and jwt_secret_ok else "degraded"
    log.info(
        "Health check completed",
        extra={"status": status, "chroma_ok": chroma_ok, "ollama_ok": ollama_ok, "jwt_secret_ok": jwt_secret_ok},
    )
    return HealthResponse(status=status, chroma_ok=chroma_ok, ollama_ok=ollama_ok, jwt_secret_ok=jwt_secret_ok)


app.include_router(auth_router)
app.include_router(ingest_router)
app.include_router(chat_router)
