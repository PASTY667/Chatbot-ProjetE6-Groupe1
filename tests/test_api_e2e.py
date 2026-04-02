import os
import sys
import unittest
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("API_ADMIN_KEY", "super-secret-admin")
os.environ.setdefault("JWT_SECRET", "unit-test-jwt-secret")
os.environ.setdefault("CHROMA_URL", "http://localhost:8001")
os.environ.setdefault("OLLAMA_URL", "http://localhost:11434")

from api.main import app
from api.auth import create_access_token
from Vector.chroma_client import get_chroma_client


class TestApiE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_pdf = PROJECT_ROOT / "ProjetChabot_CompteRenduRevue1_DomyBonnelLouboutinDomingo.pdf"
        if not cls.sample_pdf.exists():
            raise unittest.SkipTest("Sample PDF not found in repository")

        # connectivity checks (skip integration tests if unreachable)
        try:
            cls.chroma_client = get_chroma_client()
            cls.chroma_client.list_collections()
        except Exception as exc:
            raise unittest.SkipTest(f"Chroma not reachable: {exc}")

        try:
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            r = httpx.get(f"{ollama_url}/api/tags", timeout=3)
            r.raise_for_status()
        except Exception as exc:
            raise unittest.SkipTest(f"Ollama not reachable: {exc}")

        cls.client = TestClient(app)
        cls.token = create_access_token(
            "e2e-tester",
            extra_claims={
                "role": "admin",
                "permissions": ["ingest:user", "chat:query", "search:multi"],
                "doc_scope": "both",
            },
        )
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        cls.collection_name = f"test_api_e2e_{uuid4().hex}"

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "chroma_client") and hasattr(cls, "collection_name"):
            try:
                cls.chroma_client.delete_collection(name=cls.collection_name)
            except Exception:
                pass

    def test_01_ingest_sample_pdf(self):
        payload = {
            "path_file": str(self.sample_pdf),
            "collection_name": self.collection_name,
        }
        response = self.client.post("/ingest/file", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200, msg=response.text)

        data = response.json()
        self.assertEqual(data["collection_name"], self.collection_name)
        self.assertGreater(data["chunks_count"], 0)
        self.assertGreater(data["inserted_id_count"], 0)

    def test_02_chat_question_on_project_network_plan(self):
        payload = {
            "query": "quel est le plan d'adressage réseau du projet",
            "collection_name": self.collection_name,
            "k": 5,
        }
        response = self.client.post("/chat/query", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200, msg=response.text)

        data = response.json()
        self.assertIn("answer", data)
        self.assertIsInstance(data["answer"], str)
        self.assertTrue(data["answer"].strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
