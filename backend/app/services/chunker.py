import re
from typing import List, Dict, Any, Tuple


def split_text_into_chunks(
    text: str,
    chunk_size: int = 600,
    overlap: int = 100,
) -> List[str]:
    """Split clean text into overlapping chunks respecting word boundaries."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Look for sentence boundary or space to break naturally
        break_point = -1
        for sep in [". ", "? ", "! ", "\n", " "]:
            pos = text.rfind(sep, start + chunk_size // 2, end)
            if pos != -1:
                break_point = pos + len(sep)
                break

        if break_point == -1 or break_point <= start:
            break_point = end

        chunk = text[start:break_point].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward, leaving overlap
        start = max(start + 1, break_point - overlap)

    return chunks


def chunk_document_pages(
    pages: List[Tuple[int, str]],
    chunk_size: int = 600,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    """Generate ordered document chunk dictionaries with page numbers and stable indexing."""
    document_chunks: List[Dict[str, Any]] = []
    chunk_index = 0

    for page_num, page_text in pages:
        page_chunks = split_text_into_chunks(page_text, chunk_size=chunk_size, overlap=overlap)
        for chunk_text in page_chunks:
            document_chunks.append({
                "chunk_index": chunk_index,
                "content": chunk_text,
                "page_number": page_num,
                "metadata": {
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_text.split()),
                },
            })
            chunk_index += 1

    return document_chunks
