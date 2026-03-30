# api/routesChat.py
from fastapi import APIRouter, HTTPException
from api.models import ChatRequest, ChatResponse
from Vector.chroma_client import get_chroma_client, init_collection, search

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/query", response_model=ChatResponse)
def chat_query(payload: ChatRequest):
    try:
        client = get_chroma_client()
        collection = init_collection(client, payload.collection_name)
        res = search(collection, query=payload.query, k=payload.k)

        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]

        # MVP : réponse simple "extractive"
        answer = "Je me base sur les passages retrouvés dans la base documentaire."

        return ChatResponse(
            answer=answer,
            contexts=docs,
            metadatas=metas,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {e}")