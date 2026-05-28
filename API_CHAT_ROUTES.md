# Documentation des Routes Chat de l'API Franklin

## Vue d'ensemble

L'API Franklin utilise **FastAPI** et expose des routes de chat basées sur une architecture **RAG (Retrieval-Augmented Generation)**. Les routes permettent d'interroger des documents stockés dans des collections Chroma et de générer des réponses via Ollama.

**Base URL :** `http://localhost:8000` (par défaut)

**Préfixe des routes chat :** `/chat`

---

## Authentification

Toutes les routes chat **nécessitent une authentification JWT Bearer**.

### Obtenir un token JWT

**Endpoint :** `POST /auth/token`

**Request :**
```json
{
  "api_key": "your_admin_api_key",
  "subject": "service-account"
}
```

**Parameters :**
| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `api_key` | string | ✅ | Clé API administrateur (min. 8 caractères) |
| `subject` | string | ❌ | Sujet du token (défaut: "service-account") |

**Response (200 OK) :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Erreurs :**
- `401 Unauthorized` : Clé API invalide

---

## Routes Chat

### 1. POST `/chat/query` - Requête Chat Synchrone

Exécute une requête de chat et retourne la réponse complète avec les contextes utilisés.

**URL :** `POST http://localhost:8000/chat/query`

**Headers :**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body :**
```json
{
  "query": "Quelle est la politique de congés?",
  "k": 5,
  "use_official": true,
  "include_user_collection": true,
  "chat_id": "chat_123",
  "user_collection_name": null,
  "collection_name": null
}
```

**Parameters :**

| Paramètre | Type | Requis | Default | Description |
|-----------|------|--------|---------|-------------|
| `query` | string | ✅ | - | La question à poser (min. 2 caractères) |
| `k` | integer | ❌ | 5 | Nombre de contextes à récupérer (1-20) |
| `use_official` | boolean | ❌ | true | Inclure la collection officielle "documents_official" |
| `include_user_collection` | boolean | ❌ | true | Inclure la collection utilisateur si disponible |
| `chat_id` | string | ❌ | null | ID du chat (utilisé pour résoudre la collection utilisateur) |
| `user_collection_name` | string | ❌ | null | Nom explicite de la collection utilisateur |
| `collection_name` | string | ❌ | null | Force une collection spécifique (override les autres) |

**Response (200 OK) :**
```json
{
  "answer": "La politique de congés stipule que chaque employé a droit à 25 jours de congés payés par an...",
  "contexts": [
    "La politique de congés de l'entreprise...",
    "Les congés peuvent être pris par période de..."
  ],
  "metadatas": [
    {
      "source": "policy.pdf",
      "page": 3,
      "source_collection": "documents_official"
    },
    {
      "source": "policy.pdf",
      "page": 4,
      "source_collection": "documents_official"
    }
  ],
  "sources_used": ["documents_official"],
  "warnings": []
}
```

**Response Fields :**

| Champ | Type | Description |
|-------|------|-------------|
| `answer` | string | Réponse générée basée sur les contextes |
| `contexts` | array[string] | Les passages pertinents trouvés (max 5) |
| `metadatas` | array[object] | Métadonnées associées aux contextes (source, page, etc.) |
| `sources_used` | array[string] | Noms des collections utilisées |
| `warnings` | array[string] | Avertissements ou messages informatifs |

**Erreurs :**

| Code | Raison |
|------|--------|
| `400 Bad Request` | Aucune collection cible résolue |
| `401 Unauthorized` | Token manquant, invalide ou expiré |
| `500 Internal Server Error` | Erreur lors de la récupération des contextes |
| `502 Bad Gateway` | Backend LLM (Ollama) indisponible |

**Exemple cURL :**
```bash
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quelle est la politique de congés?",
    "k": 5,
    "use_official": true
  }'
```

---

### 2. POST `/chat/query/stream` - Requête Chat Streaming

Exécute une requête de chat et retourne la réponse en **streaming** (text/plain), utile pour une expérience temps réel.

**URL :** `POST http://localhost:8000/chat/query/stream`

**Headers :**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body :** Identique à `/chat/query`

```json
{
  "query": "Explique-moi le processus d'onboarding",
  "k": 3,
  "use_official": true
}
```

**Response (200 OK) :**
```
Le processus d'onboarding se déroule en plusieurs étapes...
1. Accueil du nouvel employé...
2. Formation aux outils...
3. Présentation de l'équipe...
```

**Type de réponse :** `text/plain` (streaming)

**Notes :**
- La réponse est transmise chunk par chunk
- Utile pour afficher la réponse en temps réel dans le frontend
- En cas d'erreur, un message d'erreur est envoyé : `\n[ERREUR] génération interrompue\n`

**Erreurs :**

| Code | Raison |
|------|--------|
| `401 Unauthorized` | Token manquant, invalide ou expiré |
| `500 Internal Server Error` | Erreur lors du traitement |

**Exemple cURL :**
```bash
curl -X POST http://localhost:8000/chat/query/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explique le processus d'\''onboarding",
    "k": 3
  }' \
  --no-buffer
```

**Exemple JavaScript/Fetch :**
```javascript
async function streamChat(query, token) {
  const response = await fetch('http://localhost:8000/chat/query/stream', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      k: 5,
      use_official: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const text = decoder.decode(value);
    console.log(text); // Afficher le texte en temps réel
  }
}
```

---

## Logique de Résolution des Collections

### Comment l'API détermine quelles collections interroger :

1. **Si `collection_name` est fourni :** Force cette collection (ignore les autres paramètres)
   ```json
   {
     "query": "...",
     "collection_name": "ma_collection_custom"
   }
   ```

2. **Si pas de `collection_name` :**
   - Si `include_user_collection` est `true` :
     - Si `user_collection_name` est fourni → utilise cette collection
     - Si `chat_id` est fourni → crée le nom : `documents_user_{chat_id_normalized}`
     - Sinon → warning et non utilisée
   - Si `use_official` est `true` → ajoute `documents_official`

3. **Résultat :** Fusion des collections trouvées

### Exemples de résolution :

**Exemple 1 : Force une collection**
```json
{
  "query": "...",
  "collection_name": "documents_special"
}
```
**Collections utilisées :** `["documents_special"]`

---

**Exemple 2 : Collections par défaut**
```json
{
  "query": "...",
  "use_official": true,
  "include_user_collection": true,
  "chat_id": "client_456"
}
```
**Collections utilisées :** `["documents_official", "documents_user_client_456"]`

---

**Exemple 3 : Collection officielle seulement**
```json
{
  "query": "...",
  "use_official": true,
  "include_user_collection": false
}
```
**Collections utilisées :** `["documents_official"]`

---

## Modèles de Données

### ChatRequest
```python
class ChatRequest(BaseModel):
    query: str                      # Min: 2 caractères
    k: int = 5                      # Entre 1 et 20
    use_official: bool = True
    include_user_collection: bool = True
    chat_id: str | None = None
    user_collection_name: str | None = None
    collection_name: str | None = None
```

### ChatResponse
```python
class ChatResponse(BaseModel):
    answer: str                     # Réponse générée
    contexts: list[str]            # Passages pertinents
    metadatas: list[dict]          # Métadonnées des passages
    sources_used: list[str] = []   # Noms des collections
    warnings: list[str] = []       # Messages informatifs
```

---

## Configuration (Variables d'Environnement)

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | http://127.0.0.1:11434 | URL du serveur Ollama |
| `CHAT_MODEL` | mistral:7b | Modèle LLM à utiliser |
| `OLLAMA_GENERATE_TIMEOUT_SECONDS` | 300 | Timeout pour Ollama (secondes) |
| `JWT_EXPIRES_SECONDS` | 3600 | Durée de validité du token JWT (secondes) |
| `ALLOWED_ORIGINS` | * | Origines CORS autorisées |

---

## Cas d'Usage et Exemples

### 1. Chat simple avec documents officiels

**Requête :**
```bash
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Comment contacter le support IT?"
  }'
```

**Réponse :**
```json
{
  "answer": "Vous pouvez contacter le support IT par email...",
  "contexts": ["Pour contacter le support IT..."],
  "sources_used": ["documents_official"],
  "warnings": []
}
```

---

### 2. Chat avec documents spécifiques d'un utilisateur

**Requête :**
```bash
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Résume mon rapport mensuel",
    "chat_id": "user_789",
    "include_user_collection": true,
    "k": 10
  }'
```

**Réponse :**
```json
{
  "answer": "Votre rapport mensuel résumé...",
  "contexts": ["...", "..."],
  "sources_used": ["documents_official", "documents_user_user_789"],
  "warnings": []
}
```

---

### 3. Streaming en temps réel

**Requête JavaScript :**
```javascript
async function chatStream(question) {
  const token = localStorage.getItem('authToken');
  
  const response = await fetch('/chat/query/stream', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: question,
      k: 5,
      use_official: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    document.getElementById('response').innerHTML += chunk;
  }
}
```

---

## Gestion des Erreurs

### Exemple d'erreur 401 (Token invalide)

**Requête :**
```bash
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer invalid_token" \
  -d '{"query": "..."}'
```

**Réponse (401) :**
```json
{
  "detail": "Invalid token"
}
```

---

### Exemple d'erreur 502 (Ollama indisponible)

**Réponse (502) :**
```json
{
  "detail": "LLM backend unavailable: [Errno 111] Connection refused"
}
```

---

## Santé de l'API

**Endpoint :** `GET /health`

**Response (200 OK) :**
```json
{
  "status": "ok",
  "chroma_ok": true,
  "ollama_ok": true,
  "jwt_secret_ok": true
}
```

**Status possible :** `"ok"` ou `"degraded"`

---

## Flux Recommandé pour le Frontend

1. **Obtenir un token JWT**
   ```
   POST /auth/token
   ```

2. **Envoyer une requête de chat**
   - Utiliser `/chat/query` pour réponses complètes
   - Utiliser `/chat/query/stream` pour temps réel

3. **Afficher la réponse** avec les sources et métadonnées

4. **Gérer les erreurs** (401, 500, 502)

---

## Notes Techniques

- Les contextes sont **triés par pertinence** (distance croissante) et **compactés** pour éviter les doublons
- Maximum **5 contextes** retournés dans la réponse
- Les métadonnées incluent automatiquement le champ `source_collection`
- Les timestamps JWT utilisent UTC
- L'algorithme JWT est **HS256**
