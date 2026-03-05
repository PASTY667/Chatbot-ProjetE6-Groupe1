import unittest
from pathlib import Path
import sys
from utils.logger import get_logger
from Vector.Ingestion.chunking import chunking
from Vector.Ingestion.extract import extract_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_logger()

    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.sample_pdf = self.project_root / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"
        self.extracted_text = extract_file(str(self.sample_pdf))
        self.empty_text = ""
        self.none_text = None

    def test_chunking_non_empty_text(self):
        chunks = chunking(self.extracted_text)
        self.assertIsInstance(chunks, dict)
        print(chunks[0])
        self.assertIsInstance(chunks[0], list)
        self.assertEqual(len(chunks[0]), 200)
        print("PASS: test_chunking_non_empty_text")
        print(chunks)

    def test_chunking_empty_text(self):
        empty_chunks = chunking(self.empty_text)
        with self.assertRaises(ValueError):
            chunks = chunking(self.extracted_text)
        print("PASS: test_chunking_empty_text")
        print(chunks)

    def test_chunking_none_text(self):
        none_chunks = chunking(self.none_text)
        with self.assertRaises(ValueError):
            chunks = chunking(self.extracted_text)
        print("PASS: test_chunking_none_text")
        print(chunks)

    def test_count_chunks(self):
        print(chunking(self.extracted_text)[0])
        print(len(chunking(self.extracted_text)[0]))
        self.assertEqual(len(chunking(self.extracted_text)[0]), len(chunking(self.extracted_text)[1]))


    def test_is_chunk_different(self):
        print(chunking(self.extracted_text)[0])
        print(chunking(self.extracted_text)[1])
        self.assertNotEqual(chunking(self.extracted_text)[0], chunking(self.extracted_text)[1])

if __name__ == '__main__':
    unittest.main()
