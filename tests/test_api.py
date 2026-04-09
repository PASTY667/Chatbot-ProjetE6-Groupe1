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

    @mock.patch("api.routesIngest.ingest_document")
    @mock.patch("api.routesIngest.resolve_collection_name")
    @mock.patch("api.routesIngest.save_uploaded_file")
    def test_ingest_upload_success(self, mock_save, mock_resolve_collection, mock_ingest):
        mock_save.return_value = Path("/data/users/chat_arthur_001/projet.pdf")
        mock_resolve_collection.return_value = "documents_user_chat_arthur_001"
        mock_ingest.return_value = {
            "collection_name": "documents_user_chat_arthur_001",
            "doc_id": "doc-upload-1",
            "chunks_count": 2,
            "inserted_id_count": 2,
            "source_path": "/data/users/chat_arthur_001/projet.pdf",
        }

        token = create_access_token("tester")
        response = self.client.post(
            "/ingest/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("projet.pdf", b"dummy pdf content", "application/pdf")},
            data={"scope": "user", "chat_id": "chat_arthur_001"},
        )
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(response.json()["doc_id"], "doc-upload-1")
        mock_save.assert_called_once()
        mock_ingest.assert_called_once()

    @mock.patch("api.main.get_chroma_client", side_effect=RuntimeError("no chroma"))
    @mock.patch("api.main.httpx.get", side_effect=RuntimeError("no ollama"))
    def test_health_degraded(self, _mock_ollama, _mock_chroma):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "degraded")

    @mock.patch("api.routesChat.search")
    @mock.patch("api.routesChat.init_collection")
    @mock.patch("api.routesChat.get_chroma_client")
    def test_chat_stream_no_contexts(self, mock_get_client, mock_init_collection, mock_search):
        mock_get_client.return_value = object()
        mock_init_collection.return_value = object()
        mock_search.return_value = {"documents": [[]], "metadatas": [[]]}

        token = create_access_token("tester")
        response = self.client.post(
            "/chat/query/stream",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": "test", "collection_name": "documents", "k": 2},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("aucun passage pertinent", response.text.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
