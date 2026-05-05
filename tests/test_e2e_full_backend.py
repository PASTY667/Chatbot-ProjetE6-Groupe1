import os
import sys
import unittest
import json
import httpx
from pathlib import Path

# Configuration de l'infra
API_BASE_URL = "http://192.168.150.200:8000"
ADMIN_KEY = "sIln9RHtIfZJAdLt8djB7q5XPJ6kqXeu9cD3MuXXjwHri2yf"
OFFICIAL_COLLECTION = "documents_official"

class TestE2ERealInfra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Récupère un token valide avant de lancer les tests."""
        cls.client = httpx.Client(base_url=API_BASE_URL, timeout=30.0)
        try:
            resp = cls.client.post("/auth/token", json={
                "api_key": ADMIN_KEY,
                "subject": "e2e-test-runner"
            })
            resp.raise_for_status()
            cls.token = resp.json()["access_token"]
        except Exception as e:
            raise Exception(f"Impossible de contacter l'infra sur {API_BASE_URL}: {e}")

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    # --- TESTS DE CONNEXION ---

    def test_01_health_check(self):
        """Vérifie que l'API et Chroma sont opérationnels."""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["chroma_ok"], "Chroma DB ne répond pas sur le serveur")

    # --- TESTS DE CHAT (STREAMING RÉEL) ---

    def test_02_stream_query_official(self):
        """Vérifie que le stream fonctionne avec la vraie IA (Ollama)."""
        payload = {
            "query": "Quelles sont les routes principales de l'API ?",
            "collection_name": OFFICIAL_COLLECTION,
            "k": 3
        }

        # On utilise une requête streamée
        with self.client.stream("POST", "/chat/query/stream",
                                headers=self._headers(),
                                json=payload,
                                timeout=60.0) as resp:
            self.assertEqual(resp.status_code, 200)

            full_response = ""
            for line in resp.iter_lines():
                if line:
                    full_response += line

            print(f"\n[DEBUG STREAM] {full_response[:100]}...")
            self.assertGreater(len(full_response), 0, "L'IA a renvoyé une réponse vide")

    # --- TESTS D'INGESTION RÉELLE ---

    def test_03_upload_and_query_user_doc(self):
        """Test complet : Upload -> Attente -> Query sur document utilisateur."""
        chat_id = "e2e_test_user_999"
        file_path = Path("C:/Users/arthur.domy-bonnel/Downloads/AnnexeDocumentationAPI_ProjetChatbotGRP01_20260427.pdf")

        if not file_path.exists():
            self.skipTest(f"Fichier non trouvé pour le test E2E: {file_path}")

        # 1. Upload
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/pdf")}
            data = {"scope": "user", "chat_id": chat_id}
            up_resp = self.client.post("/ingest/upload",
                                       headers=self._headers(),
                                       data=data,
                                       files=files)

        self.assertEqual(up_resp.status_code, 200, "L'upload a échoué sur l'infra")

        # 2. Query sur ce document précis (Fusion)
        query_payload = {
            "query": "De quoi parle ce document spécifique ?",
            "include_user_collection": True,
            "chat_id": chat_id,
            "use_official": False,
            "k": 2
        }

        # On laisse un court délai pour l'indexation Chroma si nécessaire
        import time
        time.sleep(1)

        resp = self.client.post("/chat/query", headers=self._headers(), json=query_payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("sources_used", resp.json())
        self.assertTrue(any(chat_id in src for src in resp.json()["sources_used"]),
                        "La collection utilisateur n'a pas été interrogée")

    # --- TESTS DE SÉCURITÉ ---

    def test_04_wrong_token_rejection(self):
        """Vérifie que l'infra rejette bien les mauvais tokens."""
        bad_headers = {"Authorization": "Bearer token_invalide"}
        resp = self.client.post("/chat/query", headers=bad_headers, json={"query": "test"})
        self.assertEqual(resp.status_code, 401)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)