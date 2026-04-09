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
os.environ.setdefault("OLLAMA_URL", "http://127.0.0.1:11434")
os.environ.setdefault("CHAT_MODEL", "mistral:7b")
os.environ.setdefault("OLLAMA_GENERATE_TIMEOUT_SECONDS", "180")

from api.main import app
from api.auth import create_access_token
from Vector.chroma_client import get_chroma_client, init_collection, search


class TestApiLLM(unittest.TestCase):
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

        cls._ensure_ollama_and_model_or_skip()

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
    def _ensure_ollama_and_model_or_skip(cls):
        """
        On Windows, localhost may resolve in ways that cause intermittent connection refused.
        Try explicit candidates and lock the first reachable URL in OLLAMA_URL.
        """
        configured = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
        candidates = []
        for url in [configured, "http://127.0.0.1:11434", "http://localhost:11434", "http://host.docker.internal:11434"]:
            if url and url not in candidates:
                candidates.append(url)

        last_error = None
        tags = None
        for url in candidates:
            try:
                r = httpx.get(f"{url}/api/tags", timeout=3)
                r.raise_for_status()
                os.environ["OLLAMA_URL"] = url
                tags = r.json()
                break
            except Exception as exc:
                last_error = exc

        if tags is None:
            raise unittest.SkipTest(f"Ollama not reachable on {candidates}. Last error: {last_error}")

        chat_model = os.getenv("CHAT_MODEL", "mistral:7b")
        available_models = {m.get("name") for m in tags.get("models", [])}
        if chat_model not in available_models:
            raise unittest.SkipTest(
                f"Configured CHAT_MODEL '{chat_model}' not found in Ollama tags: {sorted(available_models)}"
            )

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

    def test_02_retrieve_contexts_only_dev_friendly(self):
        """
        Dev-friendly retrieval-only e2e:
        validates that relevant contexts are retrievable without waiting for LLM generation.
        """
        collection = init_collection(self.chroma_client, self.collection_name)
        res = search(collection, query="plan d'adressage réseau", k=3)
        contexts = (res.get("documents") or [[]])[0]

        self.assertGreater(len(contexts), 0)
        print(f"[E2E RETRIEVE] contexts_found={len(contexts)}")  # visible in test output

    def test_03_chat_question_on_project_network_plan(self):
        payload = {
            "query": "quel est le plan d'adressage réseau du projet",
            "collection_name": self.collection_name,
            "k": 5,
        }
        response = self.client.post("/chat/query", json=payload, headers=self.headers)

        if response.status_code == 502 and "timed out" in response.text.lower():
            self.skipTest(
                "Ollama generation timeout on this machine; increase "
                "OLLAMA_GENERATE_TIMEOUT_SECONDS for slower dev hardware."
            )

        self.assertEqual(response.status_code, 200, msg=response.text)

        data = response.json()
        self.assertIn("answer", data)
        self.assertIsInstance(data["answer"], str)
        self.assertTrue(data["answer"].strip())
        print(f"[E2E LLM ANSWER] {data['answer']}")  # visible in test output

    def test_04_chat_smoke_short_prompt_dev_friendly(self):
        """
        Short-prompt smoke test to keep local runs lighter.
        """
        payload = {
            "query": "résume en une phrase le plan réseau",
            "collection_name": self.collection_name,
            "k": 1,
        }
        response = self.client.post("/chat/query", json=payload, headers=self.headers)

        if response.status_code == 502 and "timed out" in response.text.lower():
            self.skipTest(
                "Short smoke prompt still timed out on this machine; "
                "increase OLLAMA_GENERATE_TIMEOUT_SECONDS if needed."
            )

        self.assertEqual(response.status_code, 200, msg=response.text)
        data = response.json()
        self.assertTrue(data.get("answer", "").strip())
        print(f"[E2E LLM SMOKE ANSWER] {data['answer']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
