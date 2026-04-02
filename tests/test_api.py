import logging
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
        self.auth_header = {"Authorization": f"Bearer {create_access_token('tester')}"}
        self._log_records: list[logging.LogRecord] = []
        self._log_handler = logging.Handler()
        self._log_handler.setLevel(logging.NOTSET)

        def _emit(record: logging.LogRecord):
            self._log_records.append(record)

        self._log_handler.emit = _emit  # type: ignore[method-assign]
        logging.getLogger().addHandler(self._log_handler)
        self.allow_error_logs = False

    def tearDown(self):
        logging.getLogger().removeHandler(self._log_handler)
        if not self.allow_error_logs:
            errors = [r for r in self._log_records if r.levelno >= logging.ERROR]
            if errors:
                samples = "; ".join(f"{r.levelname}: {r.getMessage()}" for r in errors[:3])
                self.fail(f"Unexpected error logs were emitted: {samples}")

    def test_issue_token_invalid_key(self):
        response = self.client.post(
            "/auth/token",
            json={"api_key": "invalid-key", "subject": "tester"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid credentials")

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

    def test_chat_requires_auth(self):
        response = self.client.post("/chat/query", json={"query": "hello", "k": 1})
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

    @mock.patch("api.routesIngest.ingest_document", side_effect=FileNotFoundError("missing file"))
    def test_ingest_not_found(self, _mock_ingest):
        response = self.client.post(
            "/ingest/file",
            json={"path_file": "/tmp/missing.pdf"},
            headers=self.auth_header,
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("missing file", response.json()["detail"])

    @mock.patch("api.routesIngest.ingest_document", side_effect=ValueError("bad input"))
    def test_ingest_value_error(self, _mock_ingest):
        response = self.client.post(
            "/ingest/file",
            json={"path_file": "/tmp/doc.pdf"},
            headers=self.auth_header,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("bad input", response.json()["detail"])

    @mock.patch("api.routesIngest.ingest_document", side_effect=RuntimeError("boom"))
    def test_ingest_unexpected_error(self, _mock_ingest):
        self.allow_error_logs = True
        response = self.client.post(
            "/ingest/file",
            json={"path_file": "/tmp/doc.pdf"},
            headers=self.auth_header,
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Ingestion failure", response.json()["detail"])

    @mock.patch("api.main.get_chroma_client", side_effect=RuntimeError("no chroma"))
    @mock.patch("api.main.httpx.get", side_effect=RuntimeError("no ollama"))
    def test_health_degraded(self, _mock_ollama, _mock_chroma):
        self.allow_error_logs = True
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "degraded")

    @mock.patch("api.main.get_jwt_secret", return_value="secret")
    @mock.patch("api.main.get_chroma_client")
    @mock.patch("api.main.httpx.get")
    def test_health_ok(self, mock_httpx_get, _mock_chroma, _mock_secret):
        mock_resp = mock.Mock(status_code=200, text="ok")
        mock_resp.raise_for_status.return_value = None
        mock_httpx_get.return_value = mock_resp

        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["chroma_ok"])
        self.assertTrue(data["ollama_ok"])
        self.assertTrue(data["jwt_secret_ok"])

    def test_ingest_invalid_token_signature(self):
        token = create_access_token("tester")
        bad_token = token[:-1] + ("A" if token[-1] != "A" else "B")
        response = self.client.post(
            "/ingest/file",
            json={"path_file": "/tmp/doc.pdf"},
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid token")

    @mock.patch("api.routesChat.search", return_value={"documents": [[]], "metadatas": [[]]})
    @mock.patch("api.routesChat.init_collection")
    @mock.patch("api.routesChat.get_chroma_client")
    def test_chat_no_contexts(self, _mock_client, _mock_init, _mock_search):
        response = self.client.post(
            "/chat/query",
            json={"query": "Hello", "collection_name": "documents", "k": 1},
            headers=self.auth_header,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("aucun passage", response.json()["answer"])
        self.assertEqual(response.json()["contexts"], [])

    @mock.patch("api.routesChat._generate_answer_with_ollama", side_effect=RuntimeError("llm down"))
    @mock.patch("api.routesChat.search", return_value={"documents": [["ctx"]], "metadatas": [[{"id": 1}]]})
    @mock.patch("api.routesChat.init_collection")
    @mock.patch("api.routesChat.get_chroma_client")
    def test_chat_llm_backend_error(self, _mock_client, _mock_init, _mock_search, _mock_llm):
        self.allow_error_logs = True
        response = self.client.post(
            "/chat/query",
            json={"query": "Hello", "collection_name": "documents", "k": 1},
            headers=self.auth_header,
        )
        self.assertEqual(response.status_code, 502)
        self.assertIn("LLM backend unavailable", response.json()["detail"])

    @mock.patch("api.routesChat._generate_answer_with_ollama", return_value="pong")
    @mock.patch("api.routesChat.search", return_value={"documents": [["ctx"]], "metadatas": [[{"id": 1}]]})
    @mock.patch("api.routesChat.init_collection")
    @mock.patch("api.routesChat.get_chroma_client")
    def test_chat_success(self, _mock_client, _mock_init, _mock_search, _mock_llm):
        response = self.client.post(
            "/chat/query",
            json={"query": "Hello", "collection_name": "documents", "k": 1},
            headers=self.auth_header,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["answer"], "pong")
        self.assertEqual(data["contexts"], ["ctx"])
        self.assertEqual(data["metadatas"], [{"id": 1}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
