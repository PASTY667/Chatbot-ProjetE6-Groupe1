import unittest
import sys
from pathlib import Path

from utils.logger import get_logger

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Vector.Ingestion.extract import extract_text
from Vector.Ingestion.chunking import chunk_text
import Backend.Config.settings as settings


class TestChunkingTypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.simple_pages = [{"index": 0, "text": "Hello world.\nThis is a test."}]
        cls.simple_metadata = {"filetype": "txt", "source_path": "memory"}

    def test_body_must_be_string(self):
        with self.assertRaises(TypeError):
            chunk_text(123, self.simple_pages, self.simple_metadata)

    def test_pages_must_be_list(self):
        with self.assertRaises(TypeError):
            chunk_text("ok", "not_a_list", self.simple_metadata)

    def test_metadata_must_be_dict(self):
        with self.assertRaises(TypeError):
            chunk_text("ok", [], "not_a_dict")

    def test_empty_body_rejected(self):
        with self.assertRaises(ValueError):
            chunk_text("", self.simple_pages, self.simple_metadata)


class TestChunkingSmallText(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.simple_pages = [{"index": 0, "text": "Hello world.\nThis is a test."}]
        cls.simple_metadata = {"filetype": "txt", "source_path": "memory"}
        cls.text = "Line one.\nLine two continues.\n\nAnother paragraph starts here."

    def test_single_chunk_created(self):
        chunks = chunk_text(self.text, self.simple_pages, self.simple_metadata)
        self.assertEqual(len(chunks), 1)

    def test_single_chunk_page_range(self):
        ch = chunk_text(self.text, self.simple_pages, self.simple_metadata)[0]
        self.assertEqual((ch["page_start"], ch["page_end"]), (0, 0))

    def test_single_chunk_has_metadata_offsets(self):
        ch = chunk_text(self.text, self.simple_pages, self.simple_metadata)[0]
        self.assertGreaterEqual(ch["metadata"]["char_start"], 0)

    def test_fallback_length_function_without_tiktoken(self):
        import Vector.Ingestion.chunking as ch
        original = ch.tiktoken
        ch.tiktoken = None
        try:
            chunks = ch.chunk_text("a " * 50, self.simple_pages, self.simple_metadata)
            self.assertGreaterEqual(len(chunks), 1)
        finally:
            ch.tiktoken = original

    def test_chunk_size_overflow_raises_when_limit_tiny(self):
        original_limit = settings.CHROMA_MAX_DOC_CHARS
        settings.CHROMA_MAX_DOC_CHARS = 10
        try:
            with self.assertRaises(ValueError):
                chunk_text("longword" * 50, self.simple_pages, self.simple_metadata)
        finally:
            settings.CHROMA_MAX_DOC_CHARS = original_limit


class TestChunkingPdfIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.project_root = PROJECT_ROOT
        cls.sample_pdf = cls.project_root / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"
        if not cls.sample_pdf.exists():
            raise unittest.SkipTest("Sample PDF not found in repository")
        extraction = extract_text(cls.sample_pdf)
        cls.pdf_chunks = chunk_text(extraction["body"], extraction["pages"], extraction["metadata"])

    def test_pdf_chunks_exist(self):
        self.assertIsInstance(self.pdf_chunks, list)
        self.assertGreater(len(self.pdf_chunks), 0)

    def test_pdf_chunks_size_respects_limit(self):
        within_limit = all(len(ch["text"].encode("utf-8")) <= settings.CHROMA_MAX_DOC_CHARS for ch in self.pdf_chunks)
        self.assertTrue(within_limit)

    def test_pdf_chunks_metadata_keys_present(self):
        required = {"doc_metadata", "char_start", "char_end", "overlap_with_prev"}
        all_present = all(required.issubset(ch["metadata"].keys()) for ch in self.pdf_chunks)
        self.assertTrue(all_present)

    def test_pdf_overlap_flags_consistent(self):
        overlaps = [ch["metadata"]["overlap_with_prev"] for ch in self.pdf_chunks]
        self.assertFalse(overlaps[0])
        self.assertTrue(all(overlaps[1:]))

    def test_pdf_page_offsets_non_negative(self):
        offsets_ok = all(ch["page_start"] >= 0 and ch["page_end"] >= ch["page_start"] for ch in self.pdf_chunks)
        self.assertTrue(offsets_ok)

    def test_pdf_chunk_indices_sequential(self):
        indices = [c["chunk_index"] for c in self.pdf_chunks]
        self.assertEqual(indices, list(range(len(indices))))



if __name__ == "__main__":
    unittest.main(verbosity=2)
