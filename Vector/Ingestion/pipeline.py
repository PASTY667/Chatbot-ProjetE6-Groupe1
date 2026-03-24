import utils.logger as logger
import logging as log
import time
from extract import extract_text, return_path
from chunking import chunk_text
from Core.embeddings_fn import OllamaEmbeddingFunction
from pathlib import Path

logger.get_logger()

def ingest_document(path_file):
    """
    Ingest a document into the vector store.

    This function performs the full ingestion pipeline:
    - Extract raw text from the given file
    - Split the text into semantic chunks
    - Generate embeddings for each chunk
    - Store chunks, embeddings, and metadata into the vector database (ChromaDB)

    :param path_file: Absolute or relative path to the document file (e.g., PDF) to ingest.
    :type path_file: str
    :return: A dictionary containing ingestion statistics such as document ID,
             number of chunks created, and number of embeddings stored.
    :rtype: dict
    :raises FileNotFoundError: If the provided file path does not exist.
    :raises ValueError: If text extraction or chunking fails.
    :raises Exception: If embedding generation or vector store insertion fails.
    """

    start_ts = time.time()
    log.info(f"[pipeline][ingest] started path={path_file}")
    file_path = return_path(path_file)

    if not file_path.exists():
        log.warning(f"[pipeline][ingest] missing file path={file_path}")
        raise FileNotFoundError(f"The provided file path does not exist: {file_path}")
    if not file_path.is_file():
        log.warning(f"[pipeline][ingest] path is not a file path={file_path}")
        raise ValueError(f"The provided file path is not a file: {file_path}")

    log.info(f"[pipeline][extract] started path={path_file}")
    extracted = extract_text(file_path)
    log.info(f"[pipeline][extract] finished path={path_file}")
    log.info(f"[pipeline][chunk] started path={path_file}")
    chunks = chunk_text(extracted["body"], extracted["pages"], extracted["metadata"])
    log.info(f"[pipeline][chunk] finished path={path_file} chunks={len(chunks)}")
    log.info(f"[pipeline][embed] started path={path_file}")
    EmbeddingFunction = OllamaEmbeddingFunction
    embeddings = EmbeddingFunction(chunks)
    log.info(f"[pipeline][embed] finished path={path_file} embeddings={len(embeddings)}")

    #ToDO: Store chunks into ChromaDb
    #Statistics to return
    chunk_amount = len(chunks)
    embeddings_amount = len(embeddings)
    document_name = file_path.stem





    elapsed_ms = int((time.time() - start_ts) * 1000)
    log.info(
        f"[pipeline][ingest] finished path={path_file} "
        f"doc={document_name} chunks={chunk_amount} embeddings={embeddings_amount} elapsed_ms={elapsed_ms}"
    )

    return chunk_amount, embeddings_amount, document_name
