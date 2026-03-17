import utils.logger as logger
import logging as log
from pathlib import Path
from pypdf import PdfReader
import re
import Backend.Config.settings as settings
import unicodedata
from collections import Counter


HEADER_Y = settings.HEADER_Y
FOOTER_Y = settings.FOOTER_Y
REPEAT_THRESHOLD = settings.HEADER_FOOTER_FREQ_TRESHOLD
ALLOWED_FILETYPES = settings.ALLOWED_FILETYPES

logger.get_logger()


def _clean_line(line: str) -> str:
    line = unicodedata.normalize("NFKC", line)
    line = line.replace("\r\n", "\n").replace("\r", "\n")
    line = re.sub(r"[ \t]{2,}", " ", line)
    return line.strip()

def _is_page_number(line: str) -> bool:
    return bool(re.match(r"^(page\s+\d+(\/\d+)?)$|^\d+$", line.strip(), re.IGNORECASE))



def return_path(file_path: str):
    return Path(file_path)



def extract_file_pdf(file_path):
    """
       Extract page-ordered text from a PDF, separate recurring headers/footers via
       y-position and frequency analysis, strip page numbers and hyphenation, and
       return a normalized dict with body, headers, footers, per-page text, and
       sanitized metadata. Raises ValueError when the body is empty.
       """
    reader = PdfReader(str(file_path))
    if len(reader.pages) == 0:
        raise ValueError("Empty PDF")

    all_headers, all_footers, pages = [], [], []
    # 1. Collect raw text per page using y-position
    for page in reader.pages:
        page_headers, page_footers, page_body = [], [], []

        def visitor(text, cm, tm, font_dict, font_size):
            y = tm[5]
            if y > HEADER_Y:
                page_headers.append(text)
            elif y < FOOTER_Y:
                page_footers.append(text)
            else:
                page_body.append(text)

        page.extract_text(visitor_text=visitor)

        # Clean lines; keep empties in body to preserve paragraph breaks
        page_headers = [_clean_line(l) for l in page_headers if _clean_line(l)]
        page_footers = [_clean_line(l) for l in page_footers if _clean_line(l)]
        page_body = [_clean_line(l) for l in page_body]

        all_headers.extend(page_headers)
        all_footers.extend(page_footers)

        # Remove hyphenation and page numbers in body
        joined = "\n".join(page_body)
        joined = re.sub(r"-\n(?=\w)", "", joined)  # remove broken-line hyphens
        body_lines = [l for l in joined.split("\n") if not _is_page_number(l)]

        pages.append({"index": len(pages), "text": "\n".join(body_lines)})

    page_count = len(pages)

    # 2. Detect recurring headers/footers
    def frequent_lines(lines):
        counter = Counter(lines)
        return {line for line, cnt in counter.items() if cnt / page_count > REPEAT_THRESHOLD}

    common_headers = frequent_lines(all_headers)
    common_footers = frequent_lines(all_footers)

    # 3. Remove common headers/footers from page bodies
    for page in pages:
        filtered = []
        for line in page["text"].split("\n"):
            if line in common_headers or line in common_footers or _is_page_number(line):
                continue
            filtered.append(line)
        page["text"] = "\n".join(filtered).strip()

    # 4. Rebuild global body
    body = "\n\n".join(p["text"] for p in pages if p["text"]).strip()
    if not body:
        raise ValueError("Empty PDF body after cleaning")

    # 5. Build headers/footers strings
    headers_text = "\n".join(sorted(common_headers))
    footers_text = "\n".join(sorted(common_footers))

    # 6. Normalize metadata to strings
    raw_meta = reader.metadata or {}
    metadata = {str(k): str(v) for k, v in raw_meta.items() if v is not None}
    metadata.update({
        "filetype": "pdf",
        "page_count": page_count,
        "source_path": str(file_path.resolve())
    })

    return {
        "headers": headers_text,
        "body": body,
        "footers": footers_text,
        "pages": pages,
        "metadata": metadata
    }

def extract_file_txt(file_path):
    file_path = return_path(file_path)
    with open(file_path, "rt", encoding="utf-8") as file:
        text = file.read()
    body = _clean_line(text.lstrip("\ufeff"))
    if len(body) == 0:
        log.error("Empty body found")
        raise ValueError("Empty text body")
    return {
        "headers":"",
        "body": body,
        "footers": "",
        "pages": [{"index": 0, "text": body}],
        "metadata": {
            "filetype": "txt",
            "source_path": str(file_path.resolve())
        }

    }

def extract_file_md(file_path):

    file_path = return_path(file_path)
    with open(file_path, "rt", encoding="utf-8") as file:
        md_content = file.read()
        # Remove Markdown links/images
        text = re.sub(r'!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)', '', md_content)
        # Remove Markdown formatting symbols
        text = re.sub(r'[#*_>`-]', ' ', text)
        text = _clean_line(text)
        if len(text) == 0:
            log.error("Empty markdown body found")
            raise ValueError("Empty MD content")
        log.info("Markdown file extracted")
        return {
            "headers": "",
            "body": text,
            "footers": "",
            "pages": [{"index": 0, "text": text}],
            "metadata": {
                "filetype": "md",
                "source_path": str(file_path.resolve())
            }

        }

def extract_text(file_path) :
    """
    Validate the input path, dispatch extraction by extension, and enforce a non-empty body;
    raises FileNotFoundError or ValueError on invalid inputs
    :param file_path: path to file to be extracted
    :type file_path: str
    :return: text extracted from md, text or pdf
    :rtype: str
    :raises: FileNotFoundError if file_path does not exist
    :raises: ValueError if file_path is not a file
    """
    file_path = return_path(file_path)
    if not file_path.exists():
        log.error(f"File {file_path} does not exist")
        raise FileNotFoundError(f"File {file_path} does not exist")
    if not file_path.is_file():
        log.error(f"File {file_path} is not a file")
        raise ValueError(f"{file_path} is not a file")
    extension = file_path.suffix.lower().lstrip(".")
    if not extension in ALLOWED_FILETYPES:
        log.error(f"Unsupported file type: {extension}")
        raise ValueError(f"Unsupported file type: {extension}")
    match extension:
        case "md":
            log.info("Markdown file found")
            return extract_file_md(file_path)
        case "txt":
            log.info("Text file found")
            return extract_file_txt(file_path)
        case "pdf":
            log.info("Pdf file found")
            return extract_file_pdf(file_path)
        case _:
            log.error(f"Unsupported file type: {extension}")
            raise ValueError(f"Unsupported file type: {extension}")
