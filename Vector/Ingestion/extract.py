import utils.logger as logger
import logging as log
from pathlib import Path
from pypdf import PdfReader

def extract_file(file_path):
    """
    Extract raw text from a document file.

    This function reads supported document formats (e.g., PDF) uploaded from
    the LAMP web server and returns plain text for chunking and embedding.

    :param file_path: Absolute or relative path to the document file.
    :type file_path: str
    :return: Extracted raw text content.
    :rtype: str
    :raises FileNotFoundError: If the provided file path does not exist.
    :raises ValueError: If the file cannot be parsed or yields no text.
    """
    file_path = Path(file_path)
    if file_path.suffix.lower() != ".pdf":
        log.error("the provided file path does not end with '.pdf'")
        raise ValueError(file_path)

    reader = PdfReader(str(file_path))
    text = ""
    number_pages = len(reader.pages)
    for page in range(number_pages):
        p = reader.pages[page]
        text += p.extract_text() or ""
    log.info(f"Extracted file: {file_path}")
    log.info("extracted text : " + str(text))
    if text == "":
        log.error("No text extracted for page")
        raise ValueError(f"No text extracted for page")
    text.strip()
    return text

