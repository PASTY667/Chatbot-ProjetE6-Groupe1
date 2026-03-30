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

    def test_build_chroma_payload_ids_sequential(self):
        chunks = [
            {"chunk_index": 0, "text": "a", "metadata": {"m": 1}},
            {"chunk_index": 1, "text": "b", "metadata": {"m": 2}},
        ]
        ids, _, _ = pipeline.build_chroma_payloads(chunks, "doc")
        self.assertEqual(ids, ["doc_c0", "doc_c1"])

    def test_build_chroma_payload_documents_match(self):
        chunks = [
            {"chunk_index": 0, "text": "a", "metadata": {"m": 1}},
            {"chunk_index": 1, "text": "b", "metadata": {"m": 2}},
        ]
        _, docs, _ = pipeline.build_chroma_payloads(chunks, "doc")
        self.assertEqual(docs, ["a", "b"])

    def test_build_chroma_payload_metadata_passthrough(self):
        chunks = [
            {"chunk_index": 0, "text": "a", "metadata": {"m": 1}},
            {"chunk_index": 1, "text": "b", "metadata": {"m": 2}},
        ]
        _, _, metas = pipeline.build_chroma_payloads(chunks, "doc")
        self.assertEqual(metas[0]["m"], 1)

    def test_ingest_document_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            pipeline.ingest_document("___missing___")

    def test_ingest_document_on_directory_raises(self):
        with self.assertRaises(ValueError):
            pipeline.ingest_document(str(PROJECT_ROOT))


class TestPipelineIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        import logging
        logging.getLogger().setLevel(logging.INFO)

    def _make_temp_txt(self, content="Line one.\nLine two."):
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
        tmp.write(content)
        tmp.close()
        return tmp.name

    def test_ingest_document_invokes_add_documents(self):
        path = self._make_temp_txt()
        fake_collection = mock.MagicMock()
        fake_collection.name = "test_collection"

        with mock.patch.object(pipeline, "ensure_collection", return_value=fake_collection), \
             mock.patch.object(pipeline, "add_documents") as mocked_add:
            pipeline.ingest_document(path, collection_name="test_collection", doc_id="doc123")

        os.remove(path)
        self.assertTrue(mocked_add.called)

    def test_ingest_document_returns_expected_doc_id(self):
        path = self._make_temp_txt()
        fake_collection = mock.MagicMock()
        fake_collection.name = "test_collection"

        with mock.patch.object(pipeline, "ensure_collection", return_value=fake_collection), \
             mock.patch.object(pipeline, "add_documents"):
            result = pipeline.ingest_document(path, collection_name="test_collection", doc_id="doc123")

        os.remove(path)
        self.assertEqual(result["doc_id"], "doc123")

    def test_ingest_document_reports_chunks_count(self):
        path = self._make_temp_txt()
        fake_collection = mock.MagicMock()
        fake_collection.name = "test_collection"

        with mock.patch.object(pipeline, "ensure_collection", return_value=fake_collection), \
             mock.patch.object(pipeline, "add_documents"):
            result = pipeline.ingest_document(path, collection_name="test_collection", doc_id="doc123")

        os.remove(path)
        self.assertGreater(result["chunks_count"], 0)

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
            self.assertGreater(result["inserted_id_count"], 0)
            self.assertEqual(result["doc_id"], did)


if __name__ == "__main__":
    unittest.main()
