import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from utils.logger import get_logger

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(PROJECT_ROOT))

from Vector.Ingestion import pipeline


class TestPipelineUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        import logging
        logging.getLogger().setLevel(logging.INFO)

    def test_build_chroma_payloads(self):
        chunks = [
            {"chunk_index": 0, "text": "a", "metadata": {"m": 1}},
            {"chunk_index": 1, "text": "b", "metadata": {"m": 2}},
        ]
        ids, docs, metas = pipeline.build_chroma_payloads(chunks, "doc")
        self.assertEqual(ids, ["doc_c0", "doc_c1"])
        self.assertEqual(docs, ["a", "b"])
        self.assertEqual(metas[0]["m"], 1)

    def test_ingest_document_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            pipeline.ingest_document("___missing___")


class TestPipelineIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        import logging
        logging.getLogger().setLevel(logging.INFO)

    def test_ingest_document_with_mocks(self):
        content = "Line one.\nLine two."
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write(content)
            path = tmp.name

        fake_collection = mock.MagicMock()
        fake_collection.name = "test_collection"

        with mock.patch.object(pipeline, "ensure_collection", return_value=fake_collection), \
             mock.patch.object(pipeline, "add_documents") as mocked_add:
            result = pipeline.ingest_document(path, collection_name="test_collection", doc_id="doc123")

        mocked_add.assert_called_once()
        args, kwargs = mocked_add.call_args
        # First positional arg is collection
        self.assertEqual(args[0], fake_collection)
        self.assertEqual(result["doc_id"], "doc123")
        self.assertGreater(result["chunks_count"], 0)
        os.remove(path)

    def test_ingest_real_repo_files_with_mocks(self):
        files = [
            (PROJECT_ROOT / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf", "pdf_doc"),
            (PROJECT_ROOT / "UnitTest.txt", "txt_doc"),
            (PROJECT_ROOT / "README.md", "md_doc"),
        ]
        fake_collection = mock.MagicMock()
        fake_collection.name = "test_collection"

        for fpath, did in files:
            if not fpath.exists():
                self.skipTest(f"Missing fixture {fpath}")
            with mock.patch.object(pipeline, "ensure_collection", return_value=fake_collection), \
                 mock.patch.object(pipeline, "add_documents") as mocked_add:
                result = pipeline.ingest_document(str(fpath), collection_name="test_collection", doc_id=did)
            mocked_add.assert_called_once()
            self.assertEqual(result["doc_id"], did)
            self.assertGreater(result["chunks_count"], 0)
            self.assertGreater(result["inserted_id_count"], 0)


if __name__ == "__main__":
    unittest.main()
