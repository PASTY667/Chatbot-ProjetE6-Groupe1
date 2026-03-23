#Constants

#Constants for PDF files - Heigth for headers and footers
HEADER_Y = 750

FOOTER_Y = 90

HEADER_FOOTER_FREQ_TRESHOLD = 0.5

#Constants for chunking

CHUNK_SIZE_TOKENS = 600

CHUNK_OVERLAP_TOKENS = 75             # overlap ~20%

CHROMA_MAX_DOC_CHARS = 16000          #< 16 KB per chunk

PARAGRAPH_SEPARATORS = ["\n\n"]       # priority to paragraphs

SENTENCE_SEPARATORS = [". ", "? ", "! "]  # fallback for too long paragraphs

LINE_SEPARATOR = "\n"                 # for lists / lines

WORD_SEPARATOR = " "

TABLE_GAP_THRESHOLD = 2               # number of successives spaces to detecte a table

MIN_CHUNK_TOKENS = 120                # avoid little chunks (enhances recall)

MAX_PARAGRAPH_TOKENS = 400            # After we cut by sentences

OVERLAP_STRATEGY = "sentence_tail"    # overlap mode

EMBED_BATCH_SIZE = 32                 # embedding batch

ALLOWED_FILETYPES = ["pdf", "txt", "md"]

EMBED_MODEL = "nomic-embed-text"



