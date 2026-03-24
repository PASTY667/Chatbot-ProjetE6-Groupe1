import utils.logger as logger
import logging as log
import os
import httpx
from urllib.parse import urlparse
from chromadb import HttpClient
from chromadb.config import Settings
from Core.embeddings_fn import OllamaEmbeddingFunction

logger.get_logger()


def get_chroma_client():
    """
    Initialize and return a Chroma client using CHROMA_URL from environment.
    Initialiser et retourner un client Chroma en utilisant CHROMA_URL issu de l'environnement.
    """
    env_url = os.getenv("CHROMA_URL")

    if env_url:
        candidates = [env_url]
    else:
        candidates = [
            "http://localhost:8001",
            "http://localhost:8000",
        ]

    first_real_error = None

    for url in candidates:
        try:
            hb = httpx.get(f"{url}/api/v1/heartbeat", timeout=3)
            hb.raise_for_status()
            log.info(f"[ChromaDebug] Heartbeat {url}/api/v1/heartbeat -> {hb.status_code} {hb.text}")

            parsed = urlparse(url)
            host = parsed.hostname or "localhost"
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            ssl = parsed.scheme == "https"

            settings = Settings(
                chroma_api_impl="rest",
                chroma_server_host=host,
                chroma_server_http_port=port,
                chroma_server_ssl_enabled=ssl,
                anonymized_telemetry=False,
            )

            client = HttpClient(
                host=host,
                port=port,
                ssl=ssl,
                settings=settings,
            )

            cols = client.list_collections()
            log.info(f"Chroma client initialized with {host}:{port} ssl={ssl}, collections={cols}")
            return client

        except Exception as exc:
            if first_real_error is None:
                first_real_error = exc
            log.warning(f"[ChromaDebug] Chroma unreachable at {url}: {exc}")

    raise RuntimeError(f"Failed to connect to Chroma. First error: {first_real_error}")


def init_collection(client, collection_name: str | None = None):
    """
    Create or retrieve the target Chroma collection.
    Créer ou récupérer la collection Chroma cible.

    Parameters
    ----------
    client : chromadb.HttpClient
        Existing Chroma client instance.
    collection_name : str | None, optional
        Explicit collection name; falls back to CHROMA_COLLECTION env or ``"documents"``.

    Returns
    -------
    chromadb.api.models.Collection.Collection
        The Chroma collection handle ready for CRUD/search operations.
    """
    embedding_function = OllamaEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
    )
    log.info(f"Chroma collection ready: {collection_name} (EF attached)")
    return collection


def add_documents(collection, ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]] | None = None):
    """
    Insert new chunks into the collection.
    Insérer de nouveaux chunks dans la collection.

    Upserts the provided ids, raw chunk texts, metadata, and optionally precomputed embeddings.
    Met à jour ou insère les ids fournis, les textes, les métadonnées et éventuellement les embeddings pré-calculés.

    Parameters
    ----------
    collection : chromadb.api.models.Collection.Collection
        Chroma collection handle.
    ids : list[str]
        Unique ids per chunk (aligned with documents).
    documents : list[str]
        Chunk texts to store for retrieval and display.
    metadatas : list[dict]
        Metadata dictionaries aligned with each chunk.
    embeddings : list[list[float]] | None, optional
        Optional precomputed embeddings aligned with ids.

    Raises
    ------
    ValueError
        If list lengths are inconsistent.
    """
    if not (len(ids) == len(documents) == len(metadatas)):
        raise ValueError("ids, documents, metadatas must have the same length")
    if embeddings is not None and len(embeddings) != len(ids):
        raise ValueError("embeddings length must match ids length")

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    log.info(f"Upserted {len(ids)} documents into collection.")


def update_documents(collection, ids: list[str], documents: list[str] | None = None, metadatas: list[dict] | None = None, embeddings: list[list[float]] | None = None):
    """
    Update existing chunks in the collection.
    Mettre à jour des chunks existants dans la collection.

    Performs an upsert on the given ids. Any provided field (documents, metadatas, embeddings) replaces
    stored values; omitted fields remain unchanged when supported by Chroma’s upsert semantics.
    Effectue un upsert sur les ids donnés. Les champs fournis remplacent les valeurs existantes ; les champs omis restent inchangés.

    Parameters
    ----------
    collection : chromadb.api.models.Collection.Collection
        Chroma collection handle.
    ids : list[str]
        Ids of chunks to update.
    documents : list[str] | None, optional
        Optional new chunk texts.
    metadatas : list[dict] | None, optional
        Optional new metadata dicts.
    embeddings : list[list[float]] | None, optional
        Optional new embeddings.
    """
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    log.info(f"Updated {len(ids)} documents in collection.")


def delete_documents(collection, ids: list[str]):
    """
    Delete chunks from the collection by id.
    Supprimer des chunks de la collection via leurs identifiants.

    Removes all records matching the provided ids.
    Supprime tous les enregistrements correspondant aux ids fournis.

    Parameters
    ----------
    collection : chromadb.api.models.Collection.Collection
        Chroma collection handle.
    ids : list[str]
        List of ids to remove.
    """
    collection.delete(ids=ids)
    log.info(f"Deleted {len(ids)} documents from collection.")


def search(collection, query: str, filters: dict | None = None, where_document: dict | None = None, k: int = 5):
    """
    Run a vector search (with optional metadata and document filters) against the collection.
    Exécuter une recherche vectorielle (avec filtres optionnels) sur la collection.

    Parameters
    ----------
    collection : chromadb.api.models.Collection.Collection
        Chroma collection handle.
    query : str
        User query text. Embedding is computed by the collection's embedding_function.
    filters : dict | None, optional
        Optional metadata filter (`where`) for structured filtering.
    where_document : dict | None, optional
        Optional full-text filter (`where_document`) on document content.
    k : int, optional
        Number of results to return.

    Returns
    -------
    dict
        Query result dict (ids, documents, metadatas, distances).
    """
    return collection.query(
        query_texts=[query],
        n_results=k,
        where=filters,
        where_document=where_document,
    )