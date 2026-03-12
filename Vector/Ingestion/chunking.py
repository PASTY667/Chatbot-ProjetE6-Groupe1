import utils.logger as logger
import logging as log
import Backend.Config.settings as settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from Backend.Config.settings import SENTENCE_SEPARATORS

logger.get_logger()

target_tokens = settings.CHUNK_SIZE_TOKENS
overlap_tokens = settings.CHUNK_OVERLAP_TOKENS
max_chunk_chars = settings.CHROMA_MAX_DOC_CHARS
paragraph_seps = settings.PARAGRAPH_SEPARATORS
max_paragraph_tokens = settings.MAX_PARAGRAPH_TOKENS
min_chunk_tokens = settings.MIN_CHUNK_TOKENS


def chunking(text_body: str,pages: str,metadata: dict)->list[dict]:
    """Segment cleaned document text into semantically coherent chunks sized for
    the LLM (350–450 tokens, ~75-token overlap).
    Preserves paragraph boundaries when possible and propagates page/offset metadata for
    downstream retrieval.
    :param text: cleaned document text
    :type text: str
    :return: semantically coherent chunks sized
    :rtype: list
    :raises: ValueError if text is too long
    :raises: TypeError if input is not a string
    """

    if type(text_body) != str:
        log.error("Input text_body is not a string")
        raise TypeError("Input is not a string")
    if type(pages) != str:
        log.error("Input is not a string")
        raise TypeError("Input pages is not a string")
    if type(metadata) != dict:
        log.error("Input metadata is not a dict")
        raise TypeError("Input is not a dict")
    if text_body == "":
        log.error("Input text_body is empty")
        raise ValueError("Input is an empty string")
    if pages == "":
        log.error("Input pages is empty")
        raise ValueError("Input is an empty string")
    if type(metadata) != dict:
        log.error("Input metadata is not a dict")
        raise TypeError("Input metadata is not a dict")

    #paragraph segmentation
    paragraph_splitter = RecursiveCharacterTextSplitter(
        max_chunk_chars = max_chunk_chars,
        overlap_tokens = overlap_tokens,
        separator_chars = paragraph_seps,
    )

    paragraphs = paragraph_splitter.split_text(text_body)

    #Sentences segmentation
    for paragraph in paragraphs:
        tokens = len(paragraph)//4
        if tokens > max_chunk_chars:
            sentence_splitter = RecursiveCharacterTextSplitter(
                max_chunk_chars = max_chunk_chars,
                overlap_tokens = overlap_tokens,
                separator_chars = settings.SENTENCE_SEPARATORS,
            )
            sentences = sentence_splitter.split_text(paragraph)
            pass
            #non terminé, il faudra modifier par un indice i puis ajouter les phrases à la place du paragraphe



