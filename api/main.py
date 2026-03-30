# api/main.py
from fastapi import FastAPI
from api.routesIngest import router as ingest_router
from api.routesChat import router as chat_router

app = FastAPI(title="Chatbot API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(ingest_router)
app.include_router(chat_router)