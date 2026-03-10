import utils.logger as logger
import logging as log
import unicodedata
import re
import extract as ex
from langchain_text_splitters import MarkdownTextSplitter, RecursiveCharacterTextSplitter

logger.get_logger()

def chunking(text):
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
