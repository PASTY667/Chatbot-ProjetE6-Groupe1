import utils.logger as logger
import logging as log
import Backend.Config.settings as settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken
import bisect
import re


logger.get_logger()

target_tokens = settings.CHUNK_SIZE_TOKENS
overlap_tokens = settings.CHUNK_OVERLAP_TOKENS
max_chunk_chars = settings.CHROMA_MAX_DOC_CHARS
paragraph_seps = settings.PARAGRAPH_SEPARATORS
max_paragraph_tokens = settings.MAX_PARAGRAPH_TOKENS
min_chunk_tokens = settings.MIN_CHUNK_TOKENS
separators = paragraph_seps + settings.SENTENCE_SEPARATORS + ["\n", " "]

def chunk_text(text_body: str, pages: list, metadata: dict) -> list[dict]:
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
    final_chunks = []
    chunks = []

    if type(text_body) != str:
        log.error("Input text_body is not a string")
        raise TypeError("Input is not a string")
    if type(metadata) != dict:
        log.error("Input metadata is not a dict")
        raise TypeError("Input is not a dict")
    if text_body == "":
        log.error("Input text_body is empty")
        raise ValueError("Input is an empty string")
    if type(pages) != list:
        log.error("Input pages is not a list")
        raise TypeError("Input pages is not a list")


    #paragraph segmentation
    encoding = tiktoken.get_encoding("cl100k_base")

    length_function = lambda s: len(encoding.encode(s))

    paragraph_splitter = RecursiveCharacterTextSplitter(
        chunk_size=target_tokens,
        chunk_overlap=overlap_tokens,
        separators=separators,
        length_function=length_function,
    )

    def _clean_chunk_text(text: str) -> str:
        # normalise sauts de ligne et espaces
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        # déduplication de lignes identiques successives
        lines = []
        prev = None
        for line in text.split("\n"):
            if line == prev:
                continue
            lines.append(line)
            prev = line
        text = "\n".join(lines)
        # filtrage table des matières / index
        if "table des matières" in text.lower():
            return ""

        if len(re.sub(r"[^A-Za-zÀ-ÿ]", "", text)) < 10:
            return ""
        return text.strip()

    chunks_text_raw = paragraph_splitter.split_text(text_body)
    chunks_text = []
    for c in chunks_text_raw:
        cleaned = _clean_chunk_text(c)
        if cleaned:

            lines = [l for l in cleaned.split("\n") if l.strip()]
            short_lines = [l for l in lines if len(l.split()) <= 3]
            if lines and len(short_lines) / len(lines) > 0.7:
                continue  # on exclut ces blocs très bruyants
            chunks_text.append(cleaned)

    # si tout a été filtré, on revient au split brut (minimal)
    if not chunks_text:
        chunks_text = [c.strip() for c in chunks_text_raw if c.strip()]


    for chunk in chunks_text:
        if len(chunk.encode("utf-8")) > max_chunk_chars:
            log.info("Chunk bigger than 16KB, reduction of the size needed")
            fallback_splitter = RecursiveCharacterTextSplitter(
                chunk_size=int(target_tokens / 4),
                chunk_overlap=overlap_tokens,
                separators=separators,
                length_function=length_function,
            )
            sub_chunks = fallback_splitter.split_text(chunk)
            for sc in sub_chunks:
                if len(sc.encode("utf-8")) > max_chunk_chars:
                    log.error("Chunk still bigger than 16KB")
                    raise ValueError("ChunkingError : the chunk size is bigger than 16KB.")
                final_chunks.append(sc)
        else:
            final_chunks.append(chunk)


    page_offsets = []
    cursor_pages = 0
    for p in pages:
        page_offsets.append(cursor_pages)
        cursor_pages += len(p.get("text", ""))
    if not page_offsets:
        page_offsets = [0]


    cursor_text = 0
    backtrack = overlap_tokens * 4
    for i, ch in enumerate(final_chunks):
        search_start = max(0, cursor_text - backtrack)
        start = text_body.find(ch, search_start)
        if start == -1:
            start = text_body.find(ch)  # dernier recours global
        if start == -1:
            # fallback: estimer l'offset en se basant sur le curseur courant
            log.warning("Fallback offset estimation used; chunk text not found exactly.")
            start = cursor_text
        end = start + len(ch)
        cursor_text = end


        page_start = bisect.bisect_right(page_offsets, start) - 1
        page_end = bisect.bisect_right(page_offsets, end - 1) - 1
        overlap_with_prev = i > 0

        chunks.append(
            {
                "page_start": page_start,
                "page_end": page_end,
                "chunk_index": i,
                "text": ch,
                "metadata": {
                    "doc_metadata": metadata,
                    "char_start": start,
                    "char_end": end,
                    "overlap_with_prev": overlap_with_prev,
                },
            }
        )

    if len(chunks) == 0:
        log.error("No chunks found")
        raise ValueError("No chunks found")
    return chunks






