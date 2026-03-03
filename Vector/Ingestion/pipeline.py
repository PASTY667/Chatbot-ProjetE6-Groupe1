import utils.logger as logger
import logging as log
from extract import extract_file
from chunking import chunking
from Core.embeddings import embedding
from pathlib import Path

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
    text = extract_file(path_file)
    chunks = chunking(text)
    embeddings = []
    for chunk in chunks:
        embeddings.append(embedding(chunk))


