import utils.logger as logger
import logging as log
import unicodedata
import re

def normalize_string(input_string):
    """
    Normalize a string to lower case and remove punctuation.

    :param input_string:
    :type input_string: str
    :return: normalized string
    :rtype: str
    """
    # Convert to lowercase
    normalized = input_string.lower()

    # Remove accents/diacritics
    normalized = ''.join(
        c for c in unicodedata.normalize('NFD', normalized)
        if unicodedata.category(c) != 'Mn'
    )

    # Remove numbers
    normalized = re.sub(r'\d+', '', normalized)

    # Remove punctuation
    normalized = re.sub(r'[^\w\s]', '', normalized)

    # Remove extra whitespace
    normalized = normalized.strip()

    return normalized

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
    if not text:
        raise ValueError("Input text is empty or cannot be chunked")
    if text.strip() == "":
        raise ValueError("Input text is empty or cannot be chunked")

    text = text.strip()
    text = normalize_string(text)
    text = text.split()
    log.info("chunking...")
    lenght = len(text)
    max_length_chunk = 200
    chunks = []
    i = 0
    if lenght > max_length_chunk:
        chunks.append(text)
        log.info("No chunk needed")
        return chunks

    else:
        while i < lenght :
            sub = text[i:i + max_length_chunk]
            chunk = "".join(sub)
            chunks.append(chunk)
            i += max_length_chunk
        log.info(f"Amount of chunks: {len(chunks)}")
    return chunks
