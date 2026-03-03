import unittest
from pathlib import Path
import sys
from utils.logger import get_logger
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




if __name__ == '__main__':
    unittest.main()
