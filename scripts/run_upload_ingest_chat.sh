#!/usr/bin/env bash
set -euo pipefail

# =========================
# Configurable variables
# =========================
API_BASE="${API_BASE:-http://localhost:8000}"
API_ADMIN_KEY="${API_ADMIN_KEY:-change-this-admin-key}"
SUBJECT="${SUBJECT:-arthur}"
SCOPE="${SCOPE:-user}"                           # user | official
CHAT_ID="${CHAT_ID:-chat_arthur_001}"           # required when SCOPE=user
COLLECTION_NAME="${COLLECTION_NAME:-}"           # optional override
LOCAL_FILE="${LOCAL_FILE:-}"
QUESTION="${QUESTION:-quelles sont les mesures de sécurité envisagées dans le projet ?}"
K="${K:-5}"

if [[ -z "$LOCAL_FILE" ]]; then
  echo "ERROR: set LOCAL_FILE to the document path on your machine"
  exit 1
fi
if [[ ! -f "$LOCAL_FILE" ]]; then
  echo "ERROR: file not found: $LOCAL_FILE"
  exit 1
fi
if [[ "$SCOPE" == "user" && -z "$CHAT_ID" ]]; then
  echo "ERROR: CHAT_ID is required when SCOPE=user"
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required"
  exit 1
fi


echo "[1/5] Health check"
curl -s "$API_BASE/health" | jq .

echo "[2/5] Request token"
TOKEN="$(curl -s -X POST "$API_BASE/auth/token" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\":\"$API_ADMIN_KEY\",\"subject\":\"$SUBJECT\"}" | jq -r '.access_token')"

if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
  echo "ERROR: could not obtain access_token"
  exit 1
fi

if [[ -z "$COLLECTION_NAME" ]]; then
  if [[ "$SCOPE" == "official" ]]; then
    COLLECTION_NAME="documents_official"
  else
    COLLECTION_NAME="documents_user_${CHAT_ID}"
  fi
fi

echo "[3/5] Upload + ingest"
INGEST_RESPONSE="$(curl -s -X POST "$API_BASE/ingest/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@${LOCAL_FILE}" \
  -F "scope=${SCOPE}" \
  -F "chat_id=${CHAT_ID}" \
  -F "collection_name=${COLLECTION_NAME}")"

echo "$INGEST_RESPONSE" | jq .

echo "[4/5] Ask chat question"
CHAT_RESPONSE="$(curl -s -X POST "$API_BASE/chat/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$QUESTION\",\"collection_name\":\"$COLLECTION_NAME\",\"k\":$K}")"

echo "$CHAT_RESPONSE" | jq .

echo "[5/5] LLM answer"
echo "$CHAT_RESPONSE" | jq -r '.answer'
