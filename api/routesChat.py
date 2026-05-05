import os
import json

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.auth import require_auth
from api.models import ChatRequest, ChatResponse, ErrorResponse
from Vector.chroma_client import get_chroma_client, init_collection, search

router = APIRouter(prefix="/chat", tags=["chat"])

OFFICIAL_COLLECTION = "documents_official"

def _resolve_target_collections(payload):
    warnings = []

    # Si une collection est explicitement forcée, on la respecte
    if payload.collection_name:
        return [payload.collection_name], warnings

    collections = []

    # Résoudre la collection utilisateur si demandé
    user_col = None
    if payload.include_user_collection:
        if payload.user_collection_name:
            user_col = payload.user_collection_name
        elif payload.chat_id:
            chat = payload.chat_id.strip().lower().replace(" ", "_")
            user_col = f"documents_user_{chat}"
        else:
            warnings.append(
                "User collection ignorée : chat_id et user_collection_name absents."
            )

    # Logique finale : officielle par défaut, fusion si l'utilisateur a une collection
    if user_col:
        # L'utilisateur a un document → on cherche dans les deux
        collections = [OFFICIAL_COLLECTION, user_col]
    elif payload.use_official:
        # Pas de document utilisateur → collection officielle seulement
        collections = [OFFICIAL_COLLECTION]

    if not collections:
        raise HTTPException(
            status_code=400,
            detail="Aucune collection cible résolue."
        )

    return collections, warnings

def _collect_contexts_from_collections(client, query: str, k: int, collection_names: list[str]) -> tuple[list[dict], list[str]]:
    """
    Retourne (items, warnings)
    item = {text, metadata, distance, source_collection}
    """
    items: list[dict] = []
    warnings: list[str] = []

    for cname in collection_names:
        try:
            col = init_collection(client, cname)
            res = search(col, query=query, filters=None, where_document=None, k=k)

            docs = (res.get("documents") or [[]])[0]
            metas = (res.get("metadatas") or [[]])[0]
            dists = (res.get("distances") or [[]])[0]

            for i, txt in enumerate(docs):
                if not txt:
                    continue
                md = metas[i] if i < len(metas) else {}
                dist = dists[i] if i < len(dists) else 999999.0
                if not isinstance(md, dict):
                    md = {}
                md = {**md, "source_collection": cname}

                items.append(
                    {
                        "text": txt,
                        "metadata": md,
                        "distance": float(dist) if dist is not None else 999999.0,
                        "source_collection": cname,
                    }
                )
        except Exception as exc:
            warnings.append(f"Collection '{cname}' unavailable or query failed: {exc}")

    return items, warnings

def _rank_and_compact(items: list[dict], max_contexts: int = 5) -> tuple[list[str], list[dict], list[str]]:
    if not items:
        return [], [], []

    # tri par pertinence (distance croissante)
    items_sorted = sorted(items, key=lambda x: x.get("distance", 999999.0))

    contexts: list[str] = []
    metadatas: list[dict] = []
    sources_used: list[str] = []
    seen_texts: set[str] = set()

    for it in items_sorted:
        txt = it["text"]
        if txt in seen_texts:
            continue
        seen_texts.add(txt)

        contexts.append(txt)
        metadatas.append(it.get("metadata", {}))
        src = it.get("source_collection")
        if src and src not in sources_used:
            sources_used.append(src)

        if len(contexts) >= max_contexts:
            break

    return contexts, metadatas, sources_used





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

        collection_names, warnings1 = _resolve_target_collections(payload)
        items, warnings2 = _collect_contexts_from_collections(
            client=client,
            query=payload.query,
            k=payload.k,
            collection_names=collection_names,
        )
        contexts, metadatas, sources_used = _rank_and_compact(items, max_contexts=5)

        warnings = warnings1 + warnings2

        if not contexts:
            return ChatResponse(
                answer="Je n'ai trouvé aucun passage pertinent dans les sources demandées.",
                contexts=[],
                metadatas=[],
                sources_used=sources_used,
                warnings=warnings,
            )

        try:
            answer = _generate_answer_with_ollama(payload.query, contexts)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"LLM backend unavailable: {exc}")

        return ChatResponse(
            answer=answer,
            contexts=contexts,
            metadatas=metadatas,
            sources_used=sources_used,
            warnings=warnings,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat retrieval failure: {exc}")


@router.post(
    "/query/stream",
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
@router.post("/query/stream")
def chat_query_stream(payload: ChatRequest, _auth: dict = Depends(require_auth)):
    try:
        client = get_chroma_client()

        # 1. Utiliser la logique de fusion des collections comme dans /query
        collection_names, warnings1 = _resolve_target_collections(payload)

        # 2. Collecter les contextes multi-collections
        items, warnings2 = _collect_contexts_from_collections(
            client=client,
            query=payload.query,
            k=payload.k,
            collection_names=collection_names,
        )

        # 3. Classer et compacter (Ranking)
        contexts, metadatas, sources_used = _rank_and_compact(items, max_contexts=5)

        if not contexts:
            return StreamingResponse(iter(["Je n'ai trouvé aucun passage pertinent."]), media_type="text/plain")

        chat_model = os.getenv("CHAT_MODEL", "mistral:7b")
        ollama_url, prompt = _build_prompt(payload.query, contexts)
        timeout_seconds = float(os.getenv("OLLAMA_GENERATE_TIMEOUT_SECONDS", "300"))

        def _stream():
            try:
                # On pourrait aussi envoyer les warnings au début du stream si besoin
                with httpx.Client(timeout=timeout_seconds) as stream_client:
                    with stream_client.stream(
                            "POST",
                            f"{ollama_url}/api/generate",
                            json={"model": chat_model, "prompt": prompt, "stream": True},
                    ) as resp:
                        resp.raise_for_status()
                        for line in resp.iter_lines():
                            if not line: continue
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk: yield chunk
                            if data.get("done"): break
            except Exception:
                yield "\n[ERREUR] génération interrompue\n"

        return StreamingResponse(_stream(), media_type="text/plain")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
