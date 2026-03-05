import utils.logger as logger
import logging as log
import unicodedata
import re

logger.get_logger()

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
    Split extracted text into chunks of up to 200 words.

    The input text is first cleaned/normalized, then segmented into
    word blocks for use in the RAG ingestion pipeline.

    :param text: Full raw text extracted from a document.
    :type text: str
    :return:
        Dictionary of chunks where:
        - the key is the chunk identifier (int, starting at 0),
        - the value is a list of words (list[str]) with at most 200 items.
        The last chunk may contain fewer than 200 words.
    :rtype: dict[int, list[str]]
    :raises ValueError: If the input text is empty, blank, or cannot be processed.
    """
    if not text:
        raise ValueError("Input text is empty or cannot be chunked")
    if text.strip() == "":
        raise ValueError("Input text is empty or cannot be chunked")

    text = text.strip()
    text = normalize_string(text)
    text = text.split()
    log.info("chunking...")
    length = len(text)
    max_length_chunk = 200
    amount_chunks = (length + max_length_chunk - 1) // max_length_chunk
    chunks = {}
    if length <= max_length_chunk:
        chunks[0] = [text]
        log.info("No chunk needed")
        return chunks

    else:
        for chunk_id in range(amount_chunks):
            start = chunk_id * max_length_chunk
            end = start + max_length_chunk
            chunks[chunk_id] = text[start:end]




    return chunks
