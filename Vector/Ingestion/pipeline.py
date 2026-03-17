import utils.logger as logger
import logging as log
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

    log.info(f"Ingestion of  {path_file} started.")
    file_path = return_path(path_file)

    if not file_path.exists():
        log.error(f"The provided file path does not exist: {file_path}")
        raise FileNotFoundError(f"The provided file path does not exist: {file_path}")
    if not file_path.is_file():
        log.error(f"The provided file path is not a file: {file_path}")
        raise ValueError(f"The provided file path is not a file: {file_path}")

    log.info(f"Starting the extraction of {path_file}.")
    extracted = extract_text(file_path)
    log.info(f"Finished extracting {path_file}.")
    log.info(f"Starting the chunking of {path_file}.")
    chunks = chunk_text(extracted["body"], extracted["pages"], extracted["metadata"])
    log.info(f"Finished chunking {path_file}.")
    log.info(f"Starting the embedding generation of {path_file}.")
    EmbeddingFunction = OllamaEmbeddingFunction
    embeddings = EmbeddingFunction(chunks)
    log.info(f"Finished embedding generation of {path_file}.")

    #ToDO: Store chunks into ChromaDb
    #Statistics to return
    chunk_amount = len(chunks)
    embeddings_amount = len(embeddings)

    #ToDO: Add more statistics

