import os
import httpx
import utils.logger as logger
import logging as log
import Backend.Config.settings as settings
from typing import Iterable, List
from chromadb.api.types import Documents, Embeddings, EmbeddingFunction

logger.get_logger()


class OllamaEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self):
        self.EMBED_MODEL = settings.EMBED_MODEL
        self.EMBED_BATCH_SIZE = settings.EMBED_BATCH_SIZE
        self.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

    def __call__(self, input: Documents) -> Embeddings:
        """
        Compute embeddings for a list of texts using the configured Ollama model, with local batching.
        Calculer des embeddings pour une liste de textes via le modèle Ollama configuré, avec batching local.

        Parameters
        ----------
        input : Documents
            Ordered list of input texts to embed.

        Returns
        -------
        Embeddings
            Ordered list of embedding vectors aligned with `input`.

        Raises
        ------
        httpx.HTTPError
            If an HTTP call to the Ollama endpoint fails.
        """
        if not input:
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
            for batch in _chunks(input, batch_size):
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