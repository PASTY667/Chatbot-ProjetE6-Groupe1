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

from Vector.chroma_client import (
    get_chroma_client,
    init_collection,
    add_documents,
    update_documents,
    delete_documents,
    search,
    _sanitize_metadata_for_chroma,
)
from Vector.Ingestion.extract import extract_text
from Vector.Ingestion.chunking import chunk_text


class TestChromaMetadata(unittest.TestCase):
    def test_sanitize_flatten_nested(self):
        source = {"doc_metadata": {"/Author": "Arthur", "page_count": 17}}
        out = _sanitize_metadata_for_chroma(source)
        self.assertEqual(out["doc_metadata_/Author"], "Arthur")

    def test_sanitize_keeps_scalars(self):
        source = {"char_start": 12, "score": 0.8, "active": True}
        out = _sanitize_metadata_for_chroma(source)
        self.assertTrue(all(k in out for k in ["char_start", "score", "active"]))

    def test_sanitize_non_dict_returns_empty(self):
        self.assertEqual(_sanitize_metadata_for_chroma(None), {})


class TestChromaClientIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.sample_pdf = PROJECT_ROOT / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"
        if not cls.sample_pdf.exists():
            raise unittest.SkipTest("Sample PDF not found in repository")
        os.environ.setdefault("CHROMA_URL", "http://localhost:8001")
        try:
            cls.client = get_chroma_client()
            cls.client.list_collections()
        except Exception as exc:
            raise unittest.SkipTest(f"Chroma not reachable: {exc}")

        extraction = extract_text(cls.sample_pdf)
        chunks = chunk_text(extraction["body"], extraction["pages"], extraction["metadata"])
        cls.docs = [c["text"] for c in chunks[:2]]
        cls.metas = [c["metadata"] for c in chunks[:2]]

    def _new_collection(self):
        name = f"test_{uuid4().hex}"
        return init_collection(self.client, collection_name=name), name

    def test_get_chroma_client(self):
        self.assertIsNotNone(self.client)

    def test_init_collection(self):
        col, name = self._new_collection()
        self.assertIsNotNone(col)
        self.client.delete_collection(name=name)

    def test_add_and_search(self):
        col, name = self._new_collection()
        ids = [f"{name}_c{i}" for i in range(len(self.docs))]
        add_documents(col, ids, self.docs, self.metas, embeddings=None)
        res = search(col, query="quel est le plan de nommage du réseau", filters=None, k=2)
        self.assertGreaterEqual(len(res["ids"][0]), 1)
        self.client.delete_collection(name=name)

    def test_update_documents(self):
        col, name = self._new_collection()
        ids = [f"{name}_c{i}" for i in range(len(self.docs))]
        add_documents(col, ids, self.docs, self.metas, embeddings=None)
        update_documents(col, ids=[ids[0]], metadatas=[{"tag": "updated"}])
        fetched = col.get(ids=[ids[0]])
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
