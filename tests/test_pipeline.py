import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Ensure project root in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Vector.Ingestion import pipeline


class DummyCollection:
    def __init__(self, name: str):
        self.name = name


class TestPipeline(unittest.TestCase):
    @mock.patch("Vector.Ingestion.pipeline.log")
    def test_build_chroma_payloads(self, mock_log):
        chunks = [
            {"text": "chunk-1", "metadata": {"a": 1}},
            {"text": "chunk-2", "metadata": {"b": 2}},
        ]
        ids, documents, metadatas = pipeline.build_chroma_payloads(chunks, "docX")
        self.assertEqual(ids, ["docX_c0", "docX_c1"])
        self.assertEqual(documents, ["chunk-1", "chunk-2"])
        self.assertEqual(metadatas, [{"a": 1}, {"b": 2}])
        mock_log.info.assert_called_once()

    @mock.patch("Vector.Ingestion.pipeline.log")
    @mock.patch("Vector.Ingestion.pipeline.build_chroma_payloads")
    def test_ingest_missing_file_raises_and_warns(self, mock_build_payloads, mock_log):
        with self.assertRaises(FileNotFoundError):
            pipeline.ingest_document("___missing___")
        mock_build_payloads.assert_not_called()
        mock_log.warning.assert_called_once()
        warning_msg = mock_log.warning.call_args[0][0]
        self.assertIn("does not exist", warning_msg)

    @mock.patch("Vector.Ingestion.pipeline.add_documents")
    @mock.patch("Vector.Ingestion.pipeline.ensure_collection")
    @mock.patch("Vector.Ingestion.pipeline.log")
    @mock.patch("Vector.Ingestion.chunking.chunk_text")
    @mock.patch("Vector.Ingestion.extract.extract_text")
    def test_ingest_document_happy_path(
        self,
        mock_extract_text,
        mock_chunk_text,
        _mock_log,
        mock_ensure_collection,
        mock_add_documents,
    ):
        mock_extract_text.return_value = {
            "body": "hello world",
            "pages": [{"index": 0, "text": "hello world"}],
            "metadata": {"filetype": "txt", "source_path": "/tmp/a.txt"},
        }
        mock_chunk_text.return_value = [
            {"text": "chunk A", "metadata": {"x": 1}},
            {"text": "chunk B", "metadata": {"y": 2}},
        ]
        mock_ensure_collection.return_value = DummyCollection("documents")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write("hello world")
            tmp_path = Path(tmp.name)

        try:
            result = pipeline.ingest_document(str(tmp_path), collection_name="documents", doc_id="doc123")
        finally:
            tmp_path.unlink(missing_ok=True)

        self.assertEqual(result["collection_name"], "documents")
        self.assertEqual(result["doc_id"], "doc123")
        self.assertEqual(result["chunks_count"], 2)
        self.assertEqual(result["inserted_id_count"], 2)
        mock_add_documents.assert_called_once()

    @mock.patch("Vector.Ingestion.chunking.chunk_text", side_effect=ValueError("chunk failed"))
    @mock.patch("Vector.Ingestion.pipeline.log")
    @mock.patch("Vector.Ingestion.extract.extract_text")
    def test_ingest_extract_chunk_failure_is_raised(self, mock_extract_text, _mock_log, _mock_chunk_text):
        mock_extract_text.return_value = {
            "body": "hello world",
            "pages": [{"index": 0, "text": "hello world"}],
            "metadata": {"filetype": "txt"},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write("hello world")
            tmp_path = Path(tmp.name)

        try:
            with self.assertRaises(ValueError):
                pipeline.ingest_document(str(tmp_path))
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
