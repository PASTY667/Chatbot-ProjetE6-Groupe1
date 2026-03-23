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


class TestChunking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.project_root = PROJECT_ROOT
        cls.sample_pdf = cls.project_root / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"
        cls.simple_pages = [{"index": 0, "text": "Hello world.\nThis is a test."}]
        cls.simple_metadata = {"filetype": "txt", "source_path": "memory"}

    def test_chunking_from_pdf(self):
        if not self.sample_pdf.exists():
            self.skipTest("Sample PDF not found in repository")

        extraction = extract_text(self.sample_pdf)
        chunks = chunk_text(extraction["body"], extraction["pages"], extraction["metadata"])

        # Basic assertions
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

        # Each chunk non-empty and under 16KB guard
        for i, ch in enumerate(chunks):
            self.assertIn("text", ch)
            self.assertTrue(ch["text"].strip())
            self.assertLessEqual(len(ch["text"].encode("utf-8")), settings.CHROMA_MAX_DOC_CHARS)

            # Metadata checks
            md = ch.get("metadata", {})
            self.assertIsInstance(md, dict)
            self.assertIn("doc_metadata", md)
            self.assertIn("char_start", md)
            self.assertIn("char_end", md)
            # Overlap flag consistency
            if i == 0:
                self.assertFalse(md.get("overlap_with_prev", False))
            else:
                self.assertTrue(md.get("overlap_with_prev", False))

            # Page offsets should be non-negative
            self.assertGreaterEqual(ch.get("page_start", -1), 0)
            self.assertGreaterEqual(ch.get("page_end", -1), ch.get("page_start", 0))

        # Optional debug preview (first chunk)
        first = chunks[0]
        second = chunks[1]

        print(f"chunks_count={len(chunks)} | first_chunk_index={first['chunk_index']} | "
              f"first_page_range=({first['page_start']},{first['page_end']}) | "
              f"first_text_preview={first['text'][:1200]!r}")
        print(f"chunks_count={len(chunks)} | first_chunk_index={second['chunk_index']} | "
              f"first_page_range=({second['page_start']},{second['page_end']}) | "
              f"first_text_preview={second['text'][:120]!r}")

    def test_type_validation(self):
        with self.assertRaises(TypeError):
            chunk_text(123, [], {})
        with self.assertRaises(TypeError):
            chunk_text("ok", "not_a_list", {})
        with self.assertRaises(TypeError):
            chunk_text("ok", [], "not_a_dict")

    def test_empty_body_raises(self):
        with self.assertRaises(ValueError):
            chunk_text("", self.simple_pages, self.simple_metadata)

    def test_basic_small_text_chunking(self):
        text = "Line one.\nLine two continues.\n\nAnother paragraph starts here."
        chunks = chunk_text(text, self.simple_pages, self.simple_metadata)
        self.assertEqual(len(chunks), 1)
        ch = chunks[0]
        self.assertEqual(ch["page_start"], 0)
        self.assertEqual(ch["page_end"], 0)
        self.assertIn("Line one", ch["text"])
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



if __name__ == "__main__":
    unittest.main(verbosity=2)
