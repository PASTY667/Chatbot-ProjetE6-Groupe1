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


class TestExtractPathValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.project_root = PROJECT_ROOT

    def test_missing_file_raises(self):
        missing = self.project_root / "__missing__.pdf"
        with self.assertRaises(FileNotFoundError):
            extract_text(missing)

    def test_directory_path_raises(self):
        with self.assertRaises(ValueError):
            extract_text(self.project_root)

    def test_unsupported_extension_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            with self.assertRaises(ValueError):
                extract_text(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_non_pathlike_type_raises(self):
        with self.assertRaises(TypeError):
            extract_text(123)  # type: ignore[arg-type]


class TestExtractTxtMd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.project_root = PROJECT_ROOT
        cls.repo_txt = cls.project_root / "UnitTest.txt"
        cls.repo_md = cls.project_root / "README.md"

    def _tmp_file(self, suffix: str, content: str) -> Path:
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as tmp:
            tmp.write(content)
            return Path(tmp.name)

    def test_txt_body_and_metadata(self):
        if self.repo_txt.exists():
            path = self.repo_txt
            cleanup = False
        else:
            path = self._tmp_file(".txt", "Ligne 1\n\nLigne 2")
            cleanup = True
        try:
            result = extract_text(path)
            self.assertEqual(result["metadata"].get("filetype"), "txt")
        finally:
            if cleanup:
                path.unlink(missing_ok=True)

    def test_empty_txt_raises(self):
        path = self._tmp_file(".txt", "")
        try:
            with self.assertRaises(ValueError):
                extract_text(path)
        finally:
            path.unlink(missing_ok=True)

    def test_md_body_and_metadata(self):
        if self.repo_md.exists():
            path = self.repo_md
            cleanup = False
        else:
            path = self._tmp_file(".md", "# Titre\n\nVoici **gras** et [lien](http://example.com)")
            cleanup = True
        try:
            result = extract_text(path)
            self.assertEqual(result["metadata"].get("filetype"), "md")
        finally:
            if cleanup:
                path.unlink(missing_ok=True)

    def test_empty_md_raises(self):
        path = self._tmp_file(".md", "")
        try:
            with self.assertRaises(ValueError):
                extract_text(path)
        finally:
            path.unlink(missing_ok=True)


class TestExtractPdfIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()
        cls.sample_pdf = PROJECT_ROOT / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"
        if not cls.sample_pdf.exists():
            raise unittest.SkipTest("Sample PDF not found in repository")
        cls.result = extract_text(cls.sample_pdf)

    def test_pdf_body_not_empty(self):
        self.assertTrue(bool(self.result["body"].strip()))

    def test_pdf_pages_listed(self):
        self.assertGreater(len(self.result["pages"]), 0)

    def test_pdf_metadata_filetype(self):
        self.assertEqual(self.result["metadata"].get("filetype"), "pdf")


class TestExtractionHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()

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
        self.assertTrue(
            "Chapitre 1 Introduction" in cleaned
            and "- item utile" in cleaned
            and "1.2.3" not in cleaned
            and "Table des matières" not in cleaned
        )

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
        self.assertTrue(any("se poursuit" in m for m in merged) and "- élément de liste" in merged)

    def test_toc_page_detection(self):
        lines = ["Table des matières", "1 Introduction 1", "2 Méthode 3", "3 Résultats 5"]
        self.assertTrue(ex._is_toc_page(lines, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
