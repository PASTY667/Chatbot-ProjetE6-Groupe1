import os
import httpx
from fastapi import APIRouter, Depends, HTTPException

from api.authorization import Principal, require_permission
from api.collection_policy import resolve_search_collections
from api.models import ChatRequest, ChatResponse, ErrorResponse
from Vector.chroma_client import get_chroma_client, init_collection, search

router = APIRouter(prefix="/chat", tags=["chat"])


def _generate_answer_with_ollama(query: str, contexts: list[str]) -> str:
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    chat_model = os.getenv("CHAT_MODEL", "mistral:7b")

    prompt = (
        "Tu es un assistant RAG. Réponds uniquement avec le contexte fourni.\n\n"
        f"Contexte:\n{chr(10).join('- ' + c for c in contexts[:5])}\n\n"
        f"Question: {query}\nRéponse:"
    )

    with httpx.Client(timeout=45.0) as client:
        resp = client.post(
            f"{ollama_url}/api/generate",
            json={"model": chat_model, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        return resp.json().get("response", "")


@router.post(
    "/query",
    response_model=ChatResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def chat_query(
    payload: ChatRequest,
    principal: Principal = Depends(require_permission("chat:query")),
):
    try:
        client = get_chroma_client()
        collections = resolve_search_collections(principal)

        merged_docs = []
        merged_meta = []

        for col_name in collections:
            col = init_collection(client, col_name)
            res = search(col, query=payload.query, filters=None, where_document=None, k=payload.k)
            docs = (res.get("documents") or [[]])[0]
            metas = (res.get("metadatas") or [[]])[0]
            merged_docs.extend(docs)
            merged_meta.extend(metas)

        # simple global cut (tu pourras rerank après)
        merged_docs = merged_docs[:payload.k]
        merged_meta = merged_meta[:payload.k]

        if not merged_docs:
            return ChatResponse(answer="Aucun passage pertinent trouvé.", contexts=[], metadatas=[])

        try:
            answer = _generate_answer_with_ollama(payload.query, merged_docs)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"LLM backend unavailable: {exc}")

        return ChatResponse(answer=answer, contexts=merged_docs, metadatas=merged_meta)

    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat retrieval failure: {exc}")