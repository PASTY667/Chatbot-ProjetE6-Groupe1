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
MIN_ALPHA_CHARS = 3
MAX_SYMBOL_RATIO = 0.6
MIN_LINE_LENGTH = 4

logger.get_logger()


def _clean_line(line: str) -> str:
    """
    Normalize a raw text line coming from PDF extraction.
    Normaliser une ligne de texte brute issue de l'extraction PDF.

    Parameters
    ----------
    line : str
        Raw text line with potential mixed newlines and spacing.

    Returns
    -------
    str
        Line with Unicode normalized (NFKC), CR/LF unified to ``\\n``,
        repeated spaces collapsed, and trimmed at both ends.
    """
    line = unicodedata.normalize("NFKC", line)
    line = line.replace("\r\n", "\n").replace("\r", "\n")
    line = re.sub(r"[ \t]{2,}", " ", line)
    return line.strip()

def _is_page_number(line: str) -> bool:
    """
    Check whether a line is likely to represent a standalone page number.
    Vérifier si une ligne correspond probablement à un numéro de page isolé.

    Parameters
    ----------
    line : str
        Text line to evaluate.

    Returns
    -------
    bool
        True if the line matches common page number formats (e.g. ``"3"`` or ``"Page 3/12"``), otherwise False.
    """
    return bool(re.match(r"^(page\s+\d+(\/\d+)?)$|^\d+$", line.strip(), re.IGNORECASE))


def _looks_like_list_item(line: str) -> bool:
    """
    Detect if a line starts like a list item marker.
    Détecter si une ligne commence comme un marqueur d'élément de liste.

    Parameters
    ----------
    line : str
        Text line to test.

    Returns
    -------
    bool
        True if the line begins with bullets/dashes or numeric/alpha list prefixes, otherwise False.
    """
    return bool(
        re.match(r"^\s*([-\u2022\u2023\u25CF\u25CB\u25A0•·▪]|(\d+(\.\d+)*|\w\)))\s+", line)
    )


def _looks_like_title(line: str) -> bool:
    """
    Heuristically decide if a line resembles a title or heading.
    Décider heuristiquement si une ligne ressemble à un titre ou un en-tête.

    Parameters
    ----------
    line : str
        Text line to test.

    Returns
    -------
    bool
        True for short all-caps lines or short sequences of capitalized words, otherwise False.
    """
    stripped = line.strip()
    if not stripped:
        return False
    words = stripped.split()
    if len(words) <= 10 and stripped.isupper():
        return True
    if len(words) <= 6 and all(w[0].isupper() for w in words if w):
        return True
    return False


def _is_noise_line(line: str, repeated_noise: set[str] | None = None) -> bool:
    """
    Decide whether a body line is considered noise and should be dropped.
    Déterminer si une ligne de corps est du bruit et doit être supprimée.

    Parameters
    ----------
    line : str
        Candidate body line.
    repeated_noise : set[str] | None, optional
        Lines already identified as repeating noise across pages.

    Returns
    -------
    bool
        True if the line is decorative/short/symbol-heavy/TOC-like, otherwise False.
    """
    repeated_noise = repeated_noise or set()
    stripped = line.strip()
    if not stripped:
        return False

    if stripped in repeated_noise:
        return True

    letters = len(re.findall(r"[A-Za-zÀ-ÿ]", stripped))
    non_letters = len(re.findall(r"[^A-Za-zÀ-ÿ]", stripped))
    if letters < MIN_ALPHA_CHARS:
        if not _looks_like_list_item(stripped):
            return True
    if (letters + non_letters) > 0 and non_letters / max(1, letters + non_letters) > MAX_SYMBOL_RATIO:
        if not _looks_like_list_item(stripped):
            return True
    if len(stripped) < MIN_LINE_LENGTH and not _looks_like_list_item(stripped):
        return True
    if re.match(r"^\d+(\.\d+)*\.?$|^[IVXLCM]{1,6}$", stripped):
        return True
    if re.match(r"^[•*·▪]+$", stripped):
        return True
    lowered = stripped.lower()
    if any(keyword in lowered for keyword in ["table des matières", "sommaire", "contents", "index"]):
        return True
    return False


def normalize_body_lines(lines: list[str], repeated_noise: set[str] | None = None) -> list[str]:
    """
    Clean a list of body lines by removing noise and normalizing blanks.
    Nettoyer une liste de lignes de corps en retirant le bruit et en normalisant les blancs.

    Parameters
    ----------
    lines : list[str]
        Raw body lines extracted from a page.
    repeated_noise : set[str] | None, optional
        Pre-computed set of lines to always reject.

    Returns
    -------
    list[str]
        Filtered lines where noise is removed and consecutive blank lines are deduplicated.
    """
    normalized: list[str] = []
    for line in lines:
        if _is_noise_line(line, repeated_noise):
            continue
        stripped = line.strip()
        if not stripped:
            if normalized and normalized[-1] != "":
                normalized.append("")
            continue
        normalized.append(stripped)
    return normalized


def _merge_line_fragments(prev: str, current: str) -> str:
    """
    Merge two adjacent word fragments that likely belong to the same word.
    Fusionner deux fragments adjacents qui appartiennent probablement au même mot.

    Parameters
    ----------
    prev : str
        Previous partial text.
    current : str
        Current partial text.

    Returns
    -------
    str
        Concatenated word (no space) when both fragments look like lowercase words; otherwise joined with a space.
    """
    prev_word = re.match(r"^[A-Za-zÀ-ÿ]+$", prev)
    curr_word = re.match(r"^[A-Za-zÀ-ÿ]+$", current)
    if prev_word and curr_word and prev[-1].islower() and current[0].islower():
        return prev + current
    return prev + " " + current


def _should_merge(prev: str, current: str) -> bool:
    """
    Determine if two consecutive lines should be merged into a single paragraph line.
    Déterminer si deux lignes consécutives doivent être fusionnées en une seule ligne de paragraphe.

    Parameters
    ----------
    prev : str
        Previously accumulated line buffer.
    current : str
        Next line candidate.

    Returns
    -------
    bool
        True when the current line likely continues the sentence (lowercase start, no strong punctuation break), False otherwise.
    """
    if not prev or not current:
        return False
    if _looks_like_list_item(current) or _looks_like_title(current):
        return False
    if prev.strip().endswith((".", ":", "?", "!", ";")):
        return False
    if re.match(r"^\d+[.)]", current.strip()):
        return False
    if current and current[0].isupper() and prev.strip().endswith(")"):
        return False
    if current and current[0].islower():
        return True
    return False


def merge_lines_into_paragraphs(lines: list[str]) -> list[str]:
    """
    Reconstruct paragraphs from cleaned body lines while preserving titles and list items.
    Reconstruire des paragraphes à partir des lignes nettoyées en préservant titres et listes.

    Parameters
    ----------
    lines : list[str]
        Cleaned body lines (noise already removed).

    Returns
    -------
    list[str]
        List of paragraphs or standalone list/title lines with sensible line breaks.
    """
    paragraphs: list[str] = []
    buffer = ""
    for line in lines:
        if not line.strip():
            if buffer.strip():
                paragraphs.append(buffer.strip())
                buffer = ""
            continue
        if _looks_like_list_item(line) or _looks_like_title(line):
            if buffer.strip():
                paragraphs.append(buffer.strip())
                buffer = ""
            paragraphs.append(line.strip())
            continue
        if buffer:
            if _should_merge(buffer, line):
                buffer = _merge_line_fragments(buffer, line.strip())
            else:
                buffer = buffer.strip() + "\n" + line.strip()
        else:
            buffer = line.strip()
    if buffer.strip():
        paragraphs.append(buffer.strip())
    return paragraphs


def _is_toc_page(lines: list[str], page_index: int) -> bool:
    """
    Detect whether a page is likely a table of contents and should be skipped.
    Détecter si une page est probablement une table des matières et doit être ignorée.

    Parameters
    ----------
    lines : list[str]
        Body lines of the page.
    page_index : int
        Zero-based page index in the document.

    Returns
    -------
    bool
        True if heuristics indicate a TOC (keywords, many short numbered lines, early pages), otherwise False.
    """
    if not lines:
        return False
    joined_lower = " ".join(lines).lower()
    toc_keyword = any(k in joined_lower for k in ["table des matières", "sommaire", "contents"])
    short_lines = [l for l in lines if len(l.split()) <= 6]
    numbered = sum(1 for l in lines if re.search(r"\s\d+$", l) or re.match(r"^\d+(\.\d+)*", l.strip()))
    sentence_like = sum(1 for l in lines if re.search(r"[.!?]", l))
    if toc_keyword:
        return True
    if page_index <= 1 and lines:
        if len(short_lines) / len(lines) > 0.6 and numbered >= 3 and sentence_like / len(lines) < 0.3:
            return True
    return False


def return_path(file_path: str):
    """
    Convert an input path to a ``Path`` object.
    Convertir un chemin en entrée en objet ``Path``.

    Parameters
    ----------
    file_path : str
        Raw path string.

    Returns
    -------
    pathlib.Path
        Resolved ``Path`` instance (not checked for existence here).
    """
    return Path(file_path)



def extract_file_pdf(file_path):
    """
    Extract structured text from a PDF file with multi-step cleanup.
    Extraire du texte structuré d'un PDF avec un nettoyage en plusieurs étapes.

    Parameters
    ----------
    file_path : str | pathlib.Path
        Path to a PDF file.

    Returns
    -------
    dict
        Dictionary with keys ``headers``, ``body``, ``footers``, ``pages`` (list of per-page dicts),
        and ``metadata``.

    Raises
    ------
    ValueError
        If the PDF has zero pages or yields an empty body after cleaning.
    """
    reader = PdfReader(str(file_path))
    if len(reader.pages) == 0:
        raise ValueError("Empty PDF")

    all_headers, all_footers, pages = [], [], []
    body_line_counter = Counter()
    # 1. Collect raw text per page using y-position
    for page_index, page in enumerate(reader.pages):
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
        for l in body_lines:
            if l.strip():
                body_line_counter[l] += 1

        pages.append({"index": page_index, "raw_text": "\n".join(body_lines), "body_lines": body_lines})

    page_count = len(pages)

    # 2. Detect recurring headers/footers
    def frequent_lines(lines):
        counter = Counter(lines)
        return {line for line, cnt in counter.items() if cnt / page_count > REPEAT_THRESHOLD}

    common_headers = frequent_lines(all_headers)
    common_footers = frequent_lines(all_footers)
    repeated_body_noise = {
        line for line, cnt in body_line_counter.items()
        if cnt / page_count > REPEAT_THRESHOLD and len(line.split()) <= 4
    }

    cleaned_pages = []
    # 3. Remove common headers/footers from page bodies and normalize
    for page in pages:
        filtered = []
        for line in page["body_lines"]:
            if line in common_headers or line in common_footers or _is_page_number(line):
                continue
            filtered.append(line)
        if _is_toc_page(filtered, page["index"]):
            continue
        filtered = normalize_body_lines(filtered, repeated_body_noise)
        merged_paragraphs = merge_lines_into_paragraphs(filtered)
        cleaned_text = "\n".join(merged_paragraphs).strip()
        cleaned_pages.append(
            {
                "index": page["index"],
                "text": cleaned_text,
                "raw_text": page.get("raw_text", ""),
                "cleaned_text": cleaned_text,
                "removed_headers": list(common_headers),
                "removed_footers": list(common_footers),
                "line_count": len(filtered),
            }
        )

    # 4. Rebuild global body
    body = "\n\n".join(p["text"] for p in cleaned_pages if p["text"]).strip()
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
        "pages": cleaned_pages,
        "metadata": metadata
    }

def extract_file_txt(file_path):
    """
    Extract plain text from a UTF-8 ``.txt`` file and wrap it in the standard structure.
    Extraire du texte brut d'un fichier ``.txt`` UTF-8 et le structurer au format standard.

    Parameters
    ----------
    file_path : str | pathlib.Path
        Path to a text file.

    Returns
    -------
    dict
        Extraction result with ``headers``, ``body``, ``footers``, ``pages`` and ``metadata``.

    Raises
    ------
    ValueError
        If the file is empty after cleaning.
    """

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
    """
    Extract text from a Markdown file, stripping links/images and markup symbols.
    Extraire le texte d'un fichier Markdown en retirant liens/images et symboles de mise en forme.

    Parameters
    ----------
    file_path : str | pathlib.Path
        Path to a markdown file.

    Returns
    -------
    dict
        Extraction result with ``headers``, ``body``, ``footers``, ``pages`` and ``metadata``.

    Raises
    ------
    ValueError
        If the markdown content is empty after cleaning.
    """

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
    Dispatch extraction based on file extension and validate input.
    Déléguer l'extraction selon l'extension du fichier et valider l'entrée.

    Parameters
    ----------
    file_path : str | pathlib.Path
        Path to the file to extract (supported: pdf, txt, md).

    Returns
    -------
    dict
        Structured extraction result matching the chosen extractor.

    Raises
    ------
    FileNotFoundError
        If the path does not exist.
    ValueError
        If the path is not a file or the extension is unsupported.
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
