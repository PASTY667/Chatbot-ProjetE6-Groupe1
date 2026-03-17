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
        third = chunks[2]
        print(f"chunks_count={len(chunks)} | first_chunk_index={first['chunk_index']} | "
              f"first_page_range=({first['page_start']},{first['page_end']}) | "
              f"first_text_preview={first['text'][:120]!r}")
        print(f"chunks_count={len(chunks)} | first_chunk_index={second['chunk_index']} | "
              f"first_page_range=({second['page_start']},{second['page_end']}) | "
              f"first_text_preview={second['text'][:120]!r}")
        print(f"chunks_count={len(chunks)} | first_chunk_index={third['chunk_index']} | "
              f"first_page_range=({third['page_start']},{third['page_end']}) | "
              f"first_text_preview={third['text'][:1900]!r}")



if __name__ == "__main__":
    unittest.main(verbosity=2)
