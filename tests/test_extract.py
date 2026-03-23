import unittest
import sys
import tempfile
from pathlib import Path

from utils.logger import get_logger

# Ensure project root in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Vector.Ingestion import extract as ex
from Vector.Ingestion.extract import extract_text


class TestExtractText(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.project_root = PROJECT_ROOT
        cls.sample_pdf = cls.project_root / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"
        # Optional repo fixtures (if user placed them)
        cls.repo_txt = cls.project_root / "UnitTest.txt"
        cls.repo_md = cls.project_root / "README.md"

    def _dump_result(self, label: str, result: dict):
        print(f"\n--- {label} ---")
        print(f"path: {result.get('metadata', {}).get('source_path')}")
        print(f"headers: {result.get('headers')[:80]!r}")
        body = result.get('body', '')
        preview = body if len(body) <= 400 else body[:400]
        print(f"body_preview: {preview!r}")
        print(f"body_len: {len(body)}")
        print(f"pages_count: {len(result.get('pages', []))}")
        print(f"metadata: {result.get('metadata')}")

    def test_pdf_returns_body_and_metadata(self):
        if not self.sample_pdf.exists():
            self.skipTest("Sample PDF not found in repository")
        result = extract_text(self.sample_pdf)
        self.assertIsInstance(result, dict)
        self.assertTrue(result["body"].strip())
        self.assertIsInstance(result["pages"], list)
        self.assertGreater(len(result["pages"]), 0)
        self.assertEqual(result["metadata"].get("filetype"), "pdf")
        self._dump_result("pdf_result", result)

    def test_missing_file_raises(self):
        missing = self.project_root / "__missing__.pdf"
        with self.assertRaises(FileNotFoundError):
            extract_text(missing)

    def test_unsupported_extension_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            with self.assertRaises(ValueError):
                extract_text(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_txt_body_pages_and_metadata(self):
        # Prefer real repo fixture if present
        if self.repo_txt.exists():
            tmp_path = self.repo_txt
            cleanup = False
            content = tmp_path.read_text(encoding="utf-8")
        else:
            content = "Ligne 1\n\nLigne 2"
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
                tmp.write(content)
                tmp_path = Path(tmp.name)
            cleanup = True
        try:
            result = extract_text(tmp_path)
            self.assertEqual(result["metadata"].get("filetype"), "txt")
            self.assertIsInstance(result["pages"], list)
            self.assertGreaterEqual(len(result["pages"]), 1)
            self.assertTrue(result["body"].strip())
            self._dump_result("txt_result", result)
        finally:
            if cleanup:
                tmp_path.unlink(missing_ok=True)

    def test_empty_txt_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp_path = Path(tmp.name)
        try:
            with self.assertRaises(ValueError):
                extract_text(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_md_cleaning_and_metadata(self):
        # Prefer real repo fixture if present
        if self.repo_md.exists():
            tmp_path = self.repo_md
            cleanup = False
            md = tmp_path.read_text(encoding="utf-8")
        else:
            md = "# Titre\n\nVoici un [lien](http://example.com) et **gras**."
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
                tmp.write(md)
                tmp_path = Path(tmp.name)
            cleanup = True
        try:
            result = extract_text(tmp_path)
            self.assertEqual(result["metadata"].get("filetype"), "md")
            self.assertIsInstance(result["pages"], list)
            self.assertGreaterEqual(len(result["pages"]), 1)
            self.assertTrue(result["body"].strip())
            self._dump_result("md_result", result)
        finally:
            if cleanup:
                tmp_path.unlink(missing_ok=True)

    def test_empty_md_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
            tmp_path = Path(tmp.name)
        try:
            with self.assertRaises(ValueError):
                extract_text(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_noise_line_filtering(self):
        lines = [
            "1.2.3",
            "•",
            "Table des matières",
            "Sommaire",
            "Chapitre 1 Introduction",
            "- item utile",
            "IV",
        ]
        cleaned = ex.normalize_body_lines(lines)
        self.assertIn("Chapitre 1 Introduction", cleaned)
        self.assertIn("- item utile", cleaned)
        self.assertNotIn("1.2.3", cleaned)
        self.assertNotIn("Table des matières", cleaned)
        self.assertNotIn("IV", cleaned)

    def test_paragraph_merging(self):
        lines = [
            "Ce paragraphe commence",
            "se poursuit sur la ligne suivante",
            "et se termine ici.",
            "",
            "- élément de liste",
            "Titre De Section",
        ]
        merged = ex.merge_lines_into_paragraphs(lines)
        self.assertTrue(any("se poursuit" in m for m in merged))
        self.assertIn("- élément de liste", merged)
        self.assertIn("Titre De Section", merged)

    def test_toc_page_detection(self):
        lines = ["Table des matières", "1 Introduction 1", "2 Méthode 3", "3 Résultats 5"]
        self.assertTrue(ex._is_toc_page(lines, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
