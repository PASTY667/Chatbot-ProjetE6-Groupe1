import os
import sys
import unittest
from pathlib import Path

from utils.logger import get_logger

# Ensure project root in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Core.embeddings_fn import OllamaEmbeddingFunction


class TestOllamaEmbeddingFunctionLive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        cls.project_root = PROJECT_ROOT
        cls.sample_pdf = cls.project_root / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"

    def _server_available(self) -> bool:
        import httpx
        try:
            resp = httpx.get(self.ollama_url, timeout=2.0)
            return resp.status_code < 500
        except Exception:
            return False

    def test_live_call(self):
        if not self._server_available():
            self.skipTest("Ollama server not reachable")
        ef = OllamaEmbeddingFunction()
        texts = ["Hello world", "Test embedding"]
        embeddings = ef(texts)
        self.assertEqual(len(embeddings), len(texts))
        for emb in embeddings:
            self.assertIsInstance(emb, list)
            self.assertGreater(len(emb), 100)  # dimension plausible
            # norme raisonnable (pas NaN, pas 0)
            self.assertFalse(any(x != x for x in emb))  # NaN check
            self.assertGreater(sum(abs(x) for x in emb), 0.1)

    def test_live_embed_from_pdf(self):
        if not self._server_available():
            self.skipTest("Ollama server not reachable")
        if not self.sample_pdf.exists():
            self.skipTest("Sample PDF not found in repository")

        from Vector.Ingestion.extract import extract_text
        from Vector.Ingestion.chunking import chunk_text

        extraction = extract_text(self.sample_pdf)
        chunks = chunk_text(extraction["body"], extraction["pages"], extraction["metadata"])
        texts = [c["text"] for c in chunks[:6]]  # limiter à 2 chunks pour test rapide

        ef = OllamaEmbeddingFunction()
        embeddings = ef(texts)

        self.assertEqual(len(embeddings), len(texts))
        for emb in embeddings:
            self.assertIsInstance(emb, list)
            self.assertGreater(len(emb), 100)
            self.assertFalse(any(x != x for x in emb))
            self.assertGreater(sum(abs(x) for x in emb), 0.1)

    def test_batching_order_and_size(self):
        ef = OllamaEmbeddingFunction()
        ef.EMBED_BATCH_SIZE = 2
        texts = [f"text {i}" for i in range(5)]

        # monkeypatch httpx.Client.post to avoid live calls
        import types
        import httpx

        class DummyResponse:
            def __init__(self, payload):
                self._payload = payload
            def raise_for_status(self): ...
            def json(self): return self._payload

        calls = []
        def fake_post(self, url, json):
            calls.append(json["prompt"])
            return DummyResponse({"embedding": [len(json["prompt"])]})

        original_post = httpx.Client.post
        httpx.Client.post = types.MethodType(fake_post, httpx.Client)
        try:
            embeddings = ef(texts)
        finally:
            httpx.Client.post = original_post

        self.assertEqual(len(embeddings), len(texts))
        self.assertListEqual(calls, texts)  # order preserved
        self.assertEqual(embeddings[0][0], len(texts[0]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
