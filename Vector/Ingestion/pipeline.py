import hashlib
import logging as log
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

import utils.logger as logger
from Vector.chroma_client import get_chroma_client, init_collection, add_documents

import utils.logger as logger
from Vector.chroma_client import get_chroma_client, init_collection, add_documents

import utils.logger as logger
from Vector.chroma_client import get_chroma_client, init_collection, add_documents

import utils.logger as logger
from Vector.chroma_client import get_chroma_client, init_collection, add_documents

import utils.logger as logger
from Vector.chroma_client import get_chroma_client, init_collection, add_documents

import utils.logger as logger
from Vector.chroma_client import get_chroma_client, init_collection, add_documents

import utils.logger as logger
from Vector.chroma_client import get_chroma_client, init_collection, add_documents

logger.get_logger()


def ensure_collection(collection_name: str | None = None):
    """
    Ensure a Chroma collection is available and return it.
    """
    client = get_chroma_client()
    return init_collection(client, collection_name=collection_name)


def build_chroma_payloads(chunks: list[dict], doc_id: str) -> tuple[list[str], list[str], list[dict]]:
    """
    Build ids/documents/metadatas payloads for Chroma from chunk dicts.
    """
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for i, ch in enumerate(chunks):
        ids.append(f"{doc_id}_c{i}")
        documents.append(ch["text"])
        metadatas.append(ch["metadata"])

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
    file_path: Path = Path(path_file)

    if not file_path.exists():
        log.warning(f"The provided file path does not exist: {file_path}")
        raise FileNotFoundError(f"The provided file path does not exist: {file_path}")
    if not file_path.is_file():
        log.warning(f"The provided file path is not a file: {file_path}")
        raise ValueError(f"The provided file path is not a file: {file_path}")

    from Vector.Ingestion.extract import extract_text
    from Vector.Ingestion.chunking import chunk_text

    try:
        extracted = extract_text(file_path)
        log.info(f"[pipeline] Extracted body length={len(extracted.get('body', ''))} pages={len(extracted.get('pages', []))}")
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
        log.info(f"[pipeline] Sending {len(ids)} docs to Chroma collection={getattr(collection, 'name', collection)}")
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
