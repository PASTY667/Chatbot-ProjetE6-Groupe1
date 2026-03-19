import os
import sys
import unittest
from pathlib import Path
from uuid import uuid4

from utils.logger import get_logger

# Ensure project root in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Vector.Ingestion.extract import extract_text
from Vector.Ingestion.chunking import chunk_text
from Vector.chroma_client import (
    get_chroma_client,
    init_collection,
    add_documents,
    update_documents,
    delete_documents,
    search,
)


class TestChromaClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.sample_pdf = PROJECT_ROOT / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"
        if not cls.sample_pdf.exists():
            raise unittest.SkipTest("Sample PDF not found in repository")
        # Ensure a sensible default for local testing (host mapping 8001->8000)
        os.environ.setdefault("CHROMA_URL", "http://localhost:8001")

        # debug: test raw HTTP reachability
        import httpx
        candidates = [
            os.getenv("CHROMA_URL"),
            "http://localhost:8001",
            "http://localhost:8000",
            "http://chromadb:8000",
        ]
        for url in candidates:
            if not url:
                continue
            try:
                r = httpx.get(f"{url}/api/v1/heartbeat", timeout=3)
                print(f"[DEBUG] Heartbeat {url} -> {r.status_code} {r.text}")
            except Exception as exc:
                print(f"[DEBUG] Heartbeat fail {url}: {exc}")

        # Init chroma client, skip all tests if unreachable
        try:
            cls.client = get_chroma_client()
            # simple ping via list_collections
            cls.client.list_collections()
        except Exception as exc:
            print(f"[DEBUG] Chroma init failed: {exc}")
            raise unittest.SkipTest(f"Chroma not reachable: {exc}")

        # Prepare small document from first two chunks
        extraction = extract_text(cls.sample_pdf)
        chunks = chunk_text(extraction["body"], extraction["pages"], extraction["metadata"])
        # keep only first 2 chunks to speed up
        cls.docs = [c["text"] for c in chunks[:2]]
        cls.metas = [c["metadata"] for c in chunks[:2]]

    def _new_collection(self):
        # Unique collection per test to avoid collisions
        name = f"test_{uuid4().hex}"
        return init_collection(self.client), name

    def test_get_chroma_client(self):
        self.assertIsNotNone(self.client)

    def test_init_collection(self):
        col, name = self._new_collection()
        self.assertIsNotNone(col)
        # cleanup
        self.client.delete_collection(name=name)

    def test_add_and_search(self):
        col, name = self._new_collection()
        ids = [f"{name}_c{i}" for i in range(len(self.docs))]
        add_documents(col, ids, self.docs, self.metas, embeddings=None)

        res = search(col, query="quel est le plan de nommage du réseau", filters=None, k=2)
        self.assertIn("ids", res)
        self.assertGreaterEqual(len(res["ids"][0]), 1)

        self.client.delete_collection(name=name)

    def test_update_documents(self):
        col, name = self._new_collection()
        ids = [f"{name}_c{i}" for i in range(len(self.docs))]
        add_documents(col, ids, self.docs, self.metas, embeddings=None)

        new_meta = {"tag": "updated"}
        update_documents(col, ids=[ids[0]], metadatas=[new_meta])
        fetched = col.get(ids=[ids[0]])
        self.assertIn("metadatas", fetched)
        self.assertEqual(fetched["metadatas"][0].get("tag"), "updated")

        self.client.delete_collection(name=name)

    def test_delete_documents(self):
        col, name = self._new_collection()
        ids = [f"{name}_c{i}" for i in range(len(self.docs))]
        add_documents(col, ids, self.docs, self.metas, embeddings=None)
        delete_documents(col, ids=[ids[0]])
        res = col.get(ids=[ids[0]])
        self.assertEqual(len(res.get("ids", [])), 0)
        self.client.delete_collection(name=name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
