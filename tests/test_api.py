import os
import sys
import unittest
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("API_ADMIN_KEY", "super-secret-admin")
os.environ.setdefault("JWT_SECRET", "unit-test-jwt-secret")

from api.main import app
from api.auth import create_access_token


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Hello World")

    def test_issue_token(self):
        response = self.client.post(
            "/auth/token",
            json={"api_key": "super-secret-admin", "subject": "tester"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_ingest_requires_auth(self):
        response = self.client.post("/ingest/file", json={"path_file": "dummy.pdf"})
        self.assertEqual(response.status_code, 401)

    @mock.patch("api.routesIngest.ingest_document")
    def test_ingest_success(self, mock_ingest):
        mock_ingest.return_value = {
            "collection_name": "documents",
            "doc_id": "doc-1",
            "chunks_count": 3,
            "inserted_id_count": 3,
            "source_path": "/tmp/doc.txt",
        }
        token = create_access_token(
            "tester",
            extra_claims={
                "role": "user",
                "permissions": ["ingest:user", "chat:query"],
                "doc_scope": "user",
            },
        )
        response = self.client.post(
            "/ingest/file",
            json={"path_file": "/tmp/doc.txt"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["doc_id"], "doc-1")

    @mock.patch("api.main.get_chroma_client", side_effect=RuntimeError("no chroma"))
    @mock.patch("api.main.httpx.get", side_effect=RuntimeError("no ollama"))
    def test_health_degraded(self, _mock_ollama, _mock_chroma):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "degraded")


if __name__ == "__main__":
    unittest.main(verbosity=2)
