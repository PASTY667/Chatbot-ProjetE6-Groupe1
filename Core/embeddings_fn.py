import os
import httpx
import utils.logger as logger
import logging as log
import Backend.Config.settings as settings

logger.get_logger()

class OllamaEmbeddingFunction:
    def __init__(self):
        self.EMBED_MODEL = settings.EMBED_MODEL
        self.EMBED_BATCH_SIZE = settings.EMBED_BATCH_SIZE
        self.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

    def __call__(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = []
        for text in texts:
            resp = httpx.post(
                f"{self.OLLAMA_URL}/api/embeddings",
                json={"model": self.EMBED_MODEL, "prompt": text},
                timeout=30,
            )
            resp.raise_for_status()
            embeddings.append(resp.json()["embedding"])  # un vecteur par texte
        return embeddings