import io
from typing import List, Tuple
import pypdf
import docx


def extract_pages_from_txt(content: bytes) -> List[Tuple[int, str]]:
    """Extract text from plain text file content."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin1", errors="ignore")
    return [(1, text.strip())] if text.strip() else []


def extract_pages_from_pdf(content: bytes) -> List[Tuple[int, str]]:
    """Extract page-by-page text from PDF binary content."""
    reader = pypdf.PdfReader(io.BytesIO(content))
    pages: List[Tuple[int, str]] = []
    for idx, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append((idx, page_text.strip()))
    return pages


def extract_pages_from_docx(content: bytes) -> List[Tuple[int, str]]:
    """Extract text paragraphs and tables from DOCX binary content."""
    doc = docx.Document(io.BytesIO(content))
    paragraphs: List[str] = []
    for p in doc.paragraphs:
        if p.text.strip():
            paragraphs.append(p.text.strip())

    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                paragraphs.append(row_text)

    full_text = "\n\n".join(paragraphs)
    return [(1, full_text)] if full_text else []


def parse_document(filename: str, content: bytes) -> List[Tuple[int, str]]:
    """Dispatch file content to corresponding parser based on filename extension."""
    ext = filename[filename.rfind("."):].lower() if "." in filename else ""
    if ext == ".pdf":
        return extract_pages_from_pdf(content)
    elif ext == ".docx":
        return extract_pages_from_docx(content)
    elif ext == ".txt":
        return extract_pages_from_txt(content)
    else:
        raise ValueError(f"No parser available for extension: {ext}")
