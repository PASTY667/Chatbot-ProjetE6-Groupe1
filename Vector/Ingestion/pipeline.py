import utils.logger as logger
import logging as log
from extract import extract_file
from chunking import chunking
from Core.embeddings import embeddings
from pathlib import Path

def ingest_document(path_file):
    text = extract_file(path_file)
    chunks = chunking(text)
    for chunk in chunks:
        for word in chunk:
            embedding = embeddings(word)


