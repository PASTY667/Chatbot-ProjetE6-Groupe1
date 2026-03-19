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

    The function reads connection settings (URL, auth if needed) from the
    environment (.env) and constructs a client object ready for collection
    operations. It should be called once at startup and reused across the
    pipeline to avoid recreating HTTP sessions.
    """
    candidates = [
        os.getenv("CHROMA_URL"),
        "http://localhost:8001",  # port mapped in docker-compose (8001:8000)
        "http://localhost:8000",
    ]
    last_err = None
    for url in candidates:
        if not url:
            continue
        try:
            hb = httpx.get(f"{url}/api/v1/heartbeat", timeout=3)
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

            client = HttpClient(settings=settings)
            cols = client.list_collections()  # reachability check
            log.info(f"Chroma client initialized with {host}:{port} ssl={ssl}, collections={cols}")
            return client
        except Exception as exc:
            last_err = exc
            log.warning(f"[ChromaDebug] Chroma unreachable at {url}: {exc}")
            continue
    raise RuntimeError(f"Failed to connect to Chroma. Last error: {last_err}")



def init_collection(client):
    """
    Create or retrieve the target Chroma collection.

    Uses the configured collection name (CHROMA_COLLECTION) and attaches the
    embedding function if provided (e.g., OllamaEmbeddingFunction). This
    collection will store document chunks with their embeddings and metadata.

    :param client: An existing Chroma client instance.
    :param collection_name: Name of the collection to create or load.
    :return: The Chroma collection handle.
    """
    collection_name = os.getenv("CHROMA_COLLECTION", "documents")
    hnsw_params = {
        "hnsw:space": "cosine",
        "hnsw:m": int(os.getenv("CHROMA_HNSW_M", "16")),
        "hnsw:ef_construction": int(os.getenv("CHROMA_HNSW_EF_CONSTRUCTION", "200")),
    }
    embedding_function = OllamaEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
        metadata=hnsw_params,
    )
    log.info(
        f"Chroma collection ready: {collection_name} "
        f"(EF attached, space={hnsw_params['hnsw:space']}, m={hnsw_params['hnsw:m']}, "
        f"ef_construction={hnsw_params['hnsw:ef_construction']})"
    )
    return collection


def add_documents(collection, ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]] | None = None):
    """
    Insert new chunks into the collection.

    Upserts the provided ids, raw chunk texts, metadata, and optionally
    precomputed embeddings. If an embedding_function is attached to the
    collection, the embeddings parameter can be omitted and Chroma will call
    the function automatically.

    :param collection: Chroma collection handle.
    :param ids: Unique ids per chunk (aligned with documents).
    :param documents: Chunk texts to store for retrieval and display.
    :param metadatas: Metadata dictionaries aligned with each chunk.
    :param embeddings: Optional precomputed embeddings aligned with ids.
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

    Performs an upsert on the given ids. Any provided field (documents,
    metadatas, embeddings) replaces the stored values; omitted fields remain
    unchanged when supported by Chroma’s upsert semantics.

    :param collection: Chroma collection handle.
    :param ids: Ids of chunks to update.
    :param documents: Optional new chunk texts.
    :param metadatas: Optional new metadata dicts.
    :param embeddings: Optional new embeddings.
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

    Removes all records matching the provided ids. Use with caution, as this
    permanently deletes the embeddings and metadata associated with those ids.

    :param collection: Chroma collection handle.
    :param ids: List of ids to remove.
    """
    collection.delete(ids=ids)
    log.info(f"Deleted {len(ids)} documents from collection.")

def search(collection, query: str, filters: dict | None = None, where_document: dict | None = None, k: int = 5):
    """
    Run a vector search (with optional metadata and document filters) against the collection.

    :param collection: Chroma collection handle.
    :param query: User query text. Embedding is computed by the collection's embedding_function.
    :param filters: Optional metadata filter (`where`) for structured filtering.
    :param where_document: Optional full-text filter (`where_document`) on document content.
    :param k: Number of results to return.
    :return: Query result dict (ids, documents, metadatas, distances).
    """
    return collection.query(
        query_texts=[query],
        n_results=k,
        where=filters,
        where_document=where_document,
    )
