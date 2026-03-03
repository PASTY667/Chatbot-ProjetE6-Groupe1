import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger import get_logger
from Vector.Ingestion.extract import extract_file


class TestExtractFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()

    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.sample_pdf = self.project_root / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"

    def test_extract_pdf_returns_non_empty_text(self):
        text = extract_file(self.sample_pdf)
        self.assertIsInstance(text, str)
        self.assertTrue(text.strip())
        print("PASS: test_extract_pdf_returns_non_empty_text")
        print(text)

    def test_extract_rejects_non_pdf_extension(self):
        fake_txt = self.project_root / "README.md"
        with self.assertRaises(ValueError):
            extract_file(fake_txt)
        print("PASS: test_extract_rejects_non_pdf_extension")

    def test_extract_missing_file_raises(self):
        missing_pdf = self.project_root / "__file_that_does_not_exist__.pdf"
        with self.assertRaises(FileNotFoundError):
            extract_file(missing_pdf)
        print("PASS: test_extract_missing_file_raises")


if __name__ == "__main__":
    unittest.main(verbosity=2)
