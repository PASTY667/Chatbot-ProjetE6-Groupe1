import logging as log
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException

from api.auth import require_auth
from api.models import ChatRequest, ChatResponse, ErrorResponse
from Vector.chroma_client import get_chroma_client, init_collection, search

router = APIRouter(prefix="/chat", tags=["chat"])


def _generate_answer_with_ollama(query: str, contexts: list[str]) -> str:
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    chat_model = os.getenv("CHAT_MODEL", "mistral:7b")
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

    with httpx.Client(timeout=45.0) as client:
        resp = client.post(
            f"{ollama_url}/api/generate",
            json={"model": chat_model, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")


@router.post(
    "/query",
    response_model=ChatResponse,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def chat_query(payload: ChatRequest, _auth: dict = Depends(require_auth)):
    log.info(
        "Chat query received",
        extra={"query": payload.query, "collection_name": payload.collection_name, "k": payload.k},
    )
    try:
        client = get_chroma_client()
        collection = init_collection(client, payload.collection_name)
        results = search(collection, query=payload.query, filters=None, where_document=None, k=payload.k)

        contexts = (results.get("documents") or [[]])[0]
        metadatas = (results.get("metadatas") or [[]])[0]

        if not contexts:
            log.warning("Chat query returned no contexts", extra={"collection": getattr(collection, "name", None)})
            return ChatResponse(
                answer="Je n'ai trouvé aucun passage pertinent dans la base documentaire.",
                contexts=[],
                metadatas=[],
            )

        try:
            answer = _generate_answer_with_ollama(payload.query, contexts)
        except Exception as exc:
            log.exception("LLM backend unavailable")
            raise HTTPException(status_code=502, detail=f"LLM backend unavailable: {exc}")

        log.info(
            "Chat query answered",
            extra={
                "collection": getattr(collection, "name", None),
                "contexts_returned": len(contexts),
                "metadatas_returned": len(metadatas),
            },
        )
        return ChatResponse(answer=answer, contexts=contexts, metadatas=metadatas)
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("Chat retrieval failure")
        raise HTTPException(status_code=500, detail=f"Chat retrieval failure: {exc}")
