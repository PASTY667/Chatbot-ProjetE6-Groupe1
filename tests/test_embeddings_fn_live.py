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

    def test_live_call(self):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
