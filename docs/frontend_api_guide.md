# Guide Front-End — API RAG

Ce document explique, côté Front, comment utiliser l'API pour :
- vérifier l'état des dépendances,
- s'authentifier,
- ingérer des documents,
- poser des questions (mode JSON et mode stream).

> Base URL locale par défaut : `http://localhost:8000`

---

## 1) Vue d'ensemble des routes

- `GET /health` : état de l'API et des dépendances.
- `POST /auth/token` : émission d'un token JWT.
- `POST /ingest/file` : ingestion à partir d'un chemin de fichier serveur.
- `POST /ingest/upload` : upload + ingestion.
- `POST /chat/query` : réponse complète au format JSON.
- `POST /chat/query/stream` : réponse en flux texte.

Les routes ingest/chat sont protégées : il faut envoyer
`Authorization: Bearer <token>`.

---

## 2) Authentification

### Endpoint
`POST /auth/token`

### Body JSON
```json
{
  "api_key": "<ADMIN_API_KEY>",
  "subject": "frontend-user"
}
```

### Réponse
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Exemple Front (fetch)
```js
async function getToken(apiKey) {
  const res = await fetch("http://localhost:8000/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey, subject: "frontend-user" }),
  });

  if (!res.ok) throw new Error(`Auth failed: ${res.status}`);
  return res.json();
}
```

---

## 3) Vérification santé

### Endpoint
`GET /health`

### Réponse typique
```json
{
  "status": "ok",
  "chroma_ok": true,
  "ollama_ok": true,
  "jwt_secret_ok": true
}
```

### Bonnes pratiques Front
- Appeler cette route au démarrage de l'application.
- Afficher un état "dégradé" si `status = "degraded"`.
- Désactiver temporairement les actions chat/ingest si `ollama_ok = false` ou `chroma_ok = false`.

---

## 4) Ingestion de documents

## 4.1 Upload + ingestion (recommandé)

### Endpoint
`POST /ingest/upload`

### Form-data attendue
- `file` (obligatoire)
- `scope` (`user` par défaut)
- `chat_id` (obligatoire si `scope=user`)
- `collection_name` (optionnel)
- `doc_id` (optionnel)

### Exemple Front (fetch)
```js
async function uploadAndIngest({ file, token, scope = "user", chatId, collectionName }) {
  const form = new FormData();
  form.append("file", file);
  form.append("scope", scope);
  if (chatId) form.append("chat_id", chatId);
  if (collectionName) form.append("collection_name", collectionName);

  const res = await fetch("http://localhost:8000/ingest/upload", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload/ingest failed: ${res.status}`);
  }

  return res.json();
}
```

---

## 5) Chat JSON (réponse complète)

### Endpoint
`POST /chat/query`

### Body JSON
```json
{
  "query": "Quelles sont les consignes de sécurité ?",
  "collection_name": "documents_user_chat_arthur_001",
  "k": 5
}
```

### Réponse JSON
```json
{
  "answer": "...",
  "contexts": ["..."],
  "metadatas": [{ "source": "..." }]
}
```

### Exemple Front
```js
async function askQuestion({ token, query, collectionName, k = 5 }) {
  const res = await fetch("http://localhost:8000/chat/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query, collection_name: collectionName, k }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Chat failed: ${res.status}`);
  }

  return res.json();
}
```

---

## 6) Chat Stream (réponse progressive)

### Endpoint
`POST /chat/query/stream`

### Exemple Front (fetch + ReadableStream)
```js
async function askQuestionStream({ token, query, collectionName, k = 5, onChunk }) {
  const res = await fetch("http://localhost:8000/chat/query/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query, collection_name: collectionName, k }),
  });

  if (!res.ok || !res.body) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Stream failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onChunk(decoder.decode(value, { stream: true }));
  }
}
```

---

## 7) Gestion d'erreurs côté Front

Les routes peuvent renvoyer `detail` en JSON (ex : 400 / 401 / 500 / 502).

Recommandations UI :
- **401** : token manquant/invalide/expiré → relancer login token.
- **400** : payload invalide (champ manquant, format incorrect).
- **500** : panne backend interne.
- **502** : LLM backend indisponible (Ollama).

---

## 8) Mémoire de conversation : état actuel

Actuellement, la mémoire multi-tours **n'est pas implémentée** dans l'API :
- le payload chat ne porte pas d'historique ni de `conversation_id`,
- la route effectue un retrieval sur la question courante,
- puis génère une réponse à partir des contextes récupérés.

Si vous voulez une vraie continuité conversationnelle, il faut ajouter :
1. un `conversation_id` (et éventuellement `history`) dans la requête,
2. un stockage persistant des tours (DB),
3. l'injection de l'historique dans le prompt avant génération,
4. la persistance de la réponse finale (y compris en mode stream).

---

## 9) Checklist d'intégration Front

- [ ] Appeler `/health` au démarrage.
- [ ] Authentifier via `/auth/token`.
- [ ] Stocker le token en mémoire (et gérer son expiration).
- [ ] Uploader un document via `/ingest/upload`.
- [ ] Utiliser `/chat/query/stream` pour une UX plus fluide.
- [ ] Gérer proprement les erreurs `detail`.

