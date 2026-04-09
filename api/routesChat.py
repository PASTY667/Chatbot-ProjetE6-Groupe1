import os
import json

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.auth import require_auth
from api.models import ChatRequest, ChatResponse, ErrorResponse
from Vector.chroma_client import get_chroma_client, init_collection, search

router = APIRouter(prefix="/chat", tags=["chat"])


def _generate_answer_with_ollama(query: str, contexts: list[str]) -> str:
    ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    chat_model = os.getenv("CHAT_MODEL", "mistral:7b")
    timeout_seconds = float(os.getenv("OLLAMA_GENERATE_TIMEOUT_SECONDS", "300"))
    system_prompt = (
        "Tu es un assistant RAG. Réponds uniquement avec le contexte fourni. "
        "Si le contexte est insuffisant, dis explicitement que tu ne sais pas."
    )

    formatted_context = "\n\n".join([f"- {ctx}" for ctx in contexts[:5]])
    prompt = (
        f"{system_prompt}\n\n"
        f"Contexte:\n{formatted_context}\n\n"
        f"Question: {query}\n"
        "Réponse:"
    )

    with httpx.Client(timeout=timeout_seconds) as client:
        resp = client.post(
            f"{ollama_url}/api/generate",
            json={"model": chat_model, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        data = resp.json()
    return data.get("response", "")


def _build_prompt(query: str, contexts: list[str]) -> tuple[str, str]:
    ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    system_prompt = (
        "Tu es un assistant RAG. Réponds uniquement avec le contexte fourni. "
        "Si le contexte est insuffisant, dis explicitement que tu ne sais pas."
    )
    formatted_context = "\n\n".join([f"- {ctx}" for ctx in contexts[:5]])
    prompt = (
        f"{system_prompt}\n\n"
        f"Contexte:\n{formatted_context}\n\n"
        f"Question: {query}\n"
        "Réponse:"
    )
    return ollama_url, prompt


@router.post(
    "/query",
    response_model=ChatResponse,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def chat_query(payload: ChatRequest, _auth: dict = Depends(require_auth)):
    try:
        client = get_chroma_client()
        collection = init_collection(client, payload.collection_name)
        results = search(collection, query=payload.query, filters=None, where_document=None, k=payload.k)

        contexts = (results.get("documents") or [[]])[0]
        metadatas = (results.get("metadatas") or [[]])[0]

        if not contexts:
            return ChatResponse(
                answer="Je n'ai trouvé aucun passage pertinent dans la base documentaire.",
                contexts=[],
                metadatas=[],
            )

        try:
            answer = _generate_answer_with_ollama(payload.query, contexts)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"LLM backend unavailable: {exc}")

        return ChatResponse(answer=answer, contexts=contexts, metadatas=metadatas)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat retrieval failure: {exc}")


@router.post(
    "/query/stream",
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def chat_query_stream(payload: ChatRequest, _auth: dict = Depends(require_auth)):
    try:
        client = get_chroma_client()
        collection = init_collection(client, payload.collection_name)
        results = search(collection, query=payload.query, filters=None, where_document=None, k=payload.k)

        contexts = (results.get("documents") or [[]])[0]
        if not contexts:
            return StreamingResponse(iter(["Je n'ai trouvé aucun passage pertinent dans la base documentaire."]), media_type="text/plain")

        chat_model = os.getenv("CHAT_MODEL", "mistral:7b")
        ollama_url, prompt = _build_prompt(payload.query, contexts)
        timeout_seconds = float(os.getenv("OLLAMA_GENERATE_TIMEOUT_SECONDS", "300"))

        def _stream():
            try:
                with httpx.Client(timeout=timeout_seconds) as stream_client:
                    with stream_client.stream(
                        "POST",
                        f"{ollama_url}/api/generate",
                        json={"model": chat_model, "prompt": prompt, "stream": True},
                    ) as resp:
                        resp.raise_for_status()
                        for line in resp.iter_lines():
                            if not line:
                                continue
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                            if data.get("done"):
                                break
            except Exception:
                yield "\n[ERREUR] génération interrompue (timeout ou backend indisponible)\n"

        return StreamingResponse(_stream(), media_type="text/plain")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat retrieval failure: {exc}")
