import utils.logger as logger
import logging as log
import hashlib
from pathlib import Path
from typing import List, Tuple

from Vector.Ingestion.extract import extract_text, return_path
from Vector.Ingestion.chunking import chunk_text
from Vector.chroma_client import (
    get_chroma_client,
    init_collection,
    add_documents,
    update_documents,
)

logger.get_logger()


def ensure_collection(collection_name: str | None = None):
    """
    Initialize a Chroma client and collection using the optional name.
    Initialiser un client et une collection Chroma en utilisant le nom optionnel.

    Parameters
    ----------
    collection_name : str | None, optional
        Explicit collection name; falls back to environment defaults.

    Returns
    -------
    chromadb.api.models.Collection.Collection
        Ready-to-use Chroma collection instance.
    """
    log.info(f"[pipeline] Ensuring collection. requested={collection_name or 'default(env)'}")
    client = get_chroma_client()
    collection = init_collection(client, collection_name)
    log.info(f"[pipeline] Collection ready: {getattr(collection, 'name', collection)}")
    return collection


def build_chroma_payloads(chunks: List[dict], doc_id: str) -> Tuple[List[str], List[str], List[dict]]:
    """
    Build ids, documents, and metadatas lists from chunk objects for Chroma insertion.
    Construire les listes ids, documents et métadonnées à partir des chunks pour insertion dans Chroma.

    Parameters
    ----------
    chunks : list[dict]
        Chunk objects returned by `chunk_text`.
    doc_id : str
        Stable document identifier used to prefix chunk ids.

    Returns
    -------
    tuple[list[str], list[str], list[dict]]
        Aligned lists of ids, documents, and metadatas.
    """
    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[dict] = []
    for chunk in chunks:
        cid = f"{doc_id}_{chunk['chunk_index']}"
        ids.append(cid)
        documents.append(chunk["text"])
        metadatas.append(chunk["metadata"])
    log.info(f"[pipeline] Built payloads: ids={len(ids)} documents={len(documents)} metadatas={len(metadatas)}")
    return ids, documents, metadatas


def ingest_document(path_file: str, collection_name: str | None = None, doc_id: str | None = None) -> dict:
    """
    Run the end-to-end ingestion pipeline for a single file.
    Exécuter le pipeline d’ingestion de bout en bout pour un fichier.

    Parameters
    ----------
    path_file : str
        Absolute or relative path to the file to ingest.
    collection_name : str | None, optional
        Optional target collection name.
    doc_id : str | None, optional
        Optional document identifier; hashed from path if absent.

    Returns
    -------
    dict
        Summary containing collection name, doc_id, chunk count, inserted id count, and source path.

    Raises
    ------
    FileNotFoundError
        If the path does not exist.
    ValueError
        If the path is not a file or chunking/extraction fails.
    """
    log.info(f"Ingestion of {path_file} started.")
    file_path: Path = return_path(path_file)

    if not file_path.exists():
        log.error(f"The provided file path does not exist: {file_path}")
        log.info("[pipeline] Aborting ingestion before extraction because file is missing.")
        raise FileNotFoundError(f"The provided file path does not exist: {file_path}")
    if not file_path.is_file():
        log.error(f"The provided file path is not a file: {file_path}")
        raise ValueError(f"The provided file path is not a file: {file_path}")

    try:
        extracted = extract_text(file_path)
        log.info(f"[pipeline] Extracted body length={len(extracted.get('body',''))} pages={len(extracted.get('pages',[]))}")
        chunks = chunk_text(extracted["body"], extracted["pages"], extracted["metadata"])
        log.info(f"[pipeline] Chunking produced {len(chunks)} chunks")
    except Exception:
        log.exception("[pipeline] Ingestion failed during extract/chunk phase.")
        raise

    if doc_id is None:
        doc_id = hashlib.sha256(str(file_path).encode("utf-8")).hexdigest()
    log.info(f"[pipeline] Using doc_id={doc_id}")

    ids, documents, metadatas = build_chroma_payloads(chunks, doc_id)
    try:
        collection = ensure_collection(collection_name)
        log.info(f"[pipeline] Sending {len(ids)} docs to Chroma collection={getattr(collection,'name',collection)}")
        add_documents(collection, ids=ids, documents=documents, metadatas=metadatas, embeddings=None)
        log.info(f"[pipeline] Ingestion finished for doc_id={doc_id}")
    except Exception:
        log.exception("[pipeline] Ingestion failed during Chroma upsert phase.")
        raise

    return {
        "collection_name": collection.name if hasattr(collection, "name") else collection,
        "doc_id": doc_id,
        "chunks_count": len(chunks),
        "inserted_id_count": len(ids),
        "source_path": str(file_path),
    }


def update_metadata_document(collection_name: str | None = None, ids: List[str] | None = None, metadata: List[dict] | None = None):
    """
    Update metadata for existing documents/chunks in Chroma.
    Mettre à jour les métadonnées pour des documents/chunks existants dans Chroma.

    Parameters
    ----------
    collection_name : str | None, optional
        Target collection name.
    ids : list[str] | None
        Ids to update.
    metadata : list[dict] | None
        New metadata values aligned with ids.
    """
    collection = ensure_collection(collection_name)
    log.info(f"[pipeline] Updating metadata for {len(ids or [])} ids in collection={getattr(collection,'name',collection)}")
    update_documents(collection, ids=ids or [], metadatas=metadata or [])
