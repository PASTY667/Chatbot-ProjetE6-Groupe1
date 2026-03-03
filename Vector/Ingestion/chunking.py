import utils.logger as logger
import logging as log

def chunking(text):
    """
    Split extracted document text into chunks for embedding.

    This function prepares content for the RAG pipeline by creating
    semantically sized segments (optionally with overlap) that are later
    embedded and stored in the vector database.

    :param text: Full extracted document text.
    :type text: str
    :return: List of text chunks to embed.
    :rtype: list[str]
    :raises ValueError: If the input text is empty or cannot be chunked.
    """
    log.info("chunking...")
    lenght = len(text)
    max_length_chunk = 200
    chunks = []
    if lenght > max_length_chunk:
        chunks.append(text)
        return chunks
    else:
        pass
