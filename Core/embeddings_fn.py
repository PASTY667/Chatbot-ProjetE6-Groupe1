import os
import httpx
import utils.logger as logger
import logging as log
import Backend.Config.settings as settings
from typing import Iterable, List

logger.get_logger()

class OllamaEmbeddingFunction:
    def __init__(self):
        self.EMBED_MODEL = settings.EMBED_MODEL
        self.EMBED_BATCH_SIZE = settings.EMBED_BATCH_SIZE
        self.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

    def __call__(self, texts: list[str]) -> list[list[float]]:
        """
        Compute embeddings for a list of texts using the configured Ollama model, with local batching.
        Calculer des embeddings pour une liste de textes via le modèle Ollama configuré, avec batching local.

        Parameters
        ----------
        texts : list[str]
            Ordered list of input texts to embed.

        Returns
        -------
        list[list[float]]
            Ordered list of embedding vectors aligned with `texts`.

        Raises
        ------
        httpx.HTTPError
            If an HTTP call to the Ollama endpoint fails.
        """
        if not texts:
            return []
        batch_size = max(1, int(self.EMBED_BATCH_SIZE))
        embeddings: List[List[float]] = []

        def _chunks(seq: Iterable[str], n: int):
            buf = []
            for item in seq:
                buf.append(item)
                if len(buf) == n:
                    yield buf
                    buf = []
            if buf:
                yield buf

        with httpx.Client(timeout=30.0) as client:
            for batch in _chunks(texts, batch_size):
                batch_embeddings = []
                for text in batch:
                    resp = client.post(
                        f"{self.OLLAMA_URL}/api/embeddings",
                        json={"model": self.EMBED_MODEL, "prompt": text},
                    )
                    resp.raise_for_status()
                    batch_embeddings.append(resp.json()["embedding"])
                embeddings.extend(batch_embeddings)

        return embeddings
