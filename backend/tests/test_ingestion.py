import io
import uuid
import pypdf
import docx
from sqlalchemy import select

from app.models.document import Document, DocumentStatus
from app.models.job import IngestionJob, JobStatus
from app.models.chunk import DocumentChunk
from app.models.workspace import Workspace
from app.services import parser, chunker, storage, ingestion
from tests.conftest import TestingSessionLocal


def test_txt_parser():
    content = b"This is a sample plain text document."
    pages = parser.parse_document("test.txt", content)
    assert len(pages) == 1
    assert pages[0][0] == 1
    assert "sample plain text" in pages[0][1]


def test_pdf_parser():
    # Build in-memory valid PDF using pypdf
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=72, height=72)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_content = pdf_bytes.getvalue()

    pages = parser.parse_document("sample.pdf", pdf_content)
    assert isinstance(pages, list)


def test_docx_parser():
    # Build in-memory valid DOCX
    doc = docx.Document()
    doc.add_paragraph("First paragraph of docx.")
    doc.add_paragraph("Second paragraph with important facts.")
    docx_bytes = io.BytesIO()
    doc.save(docx_bytes)
    docx_content = docx_bytes.getvalue()

    pages = parser.parse_document("sample.docx", docx_content)
    assert len(pages) == 1
    assert "First paragraph" in pages[0][1]
    assert "Second paragraph" in pages[0][1]


def test_chunker_natural_boundaries():
    text = (
        "DocuMind AI processes documents reliably. "
        "It provides evidence-grounded answers. "
        "Every answer maps to verified source citations. "
        "Multi-tenant isolation protects privacy."
    )
    pages = [(1, text)]
    chunks = chunker.chunk_document_pages(pages, chunk_size=80, overlap=20)
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk["chunk_index"] == i
        assert chunk["page_number"] == 1
        assert "char_count" in chunk["metadata"]


def test_end_to_end_ingestion_pipeline():
    db = TestingSessionLocal()
    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    doc_id = uuid.uuid4()

    ws = Workspace(id=ws_id, name="Pipeline-WS", owner_id=user_id)
    doc_text = "DocuMind AI is an intelligent question answering assistant. It retrieves verified citations."
    storage_path = f"{user_id}/{ws_id}/{doc_id}_guide.txt"
    storage.save_file(storage_path, doc_text.encode("utf-8"))

    doc = Document(
        id=doc_id,
        workspace_id=ws_id,
        owner_id=user_id,
        original_filename="guide.txt",
        storage_path=storage_path,
        mime_type="text/plain",
        size_bytes=len(doc_text),
        status=DocumentStatus.QUEUED,
    )
    job = IngestionJob(
        id=uuid.uuid4(),
        document_id=doc.id,
        workspace_id=ws_id,
        owner_id=user_id,
        status=JobStatus.QUEUED,
    )
    db.add_all([ws, doc, job])
    db.commit()

    # Process job through ingestion pipeline
    success = ingestion.process_ingestion_job(db, job)
    assert success is True

    # Verify job completed and document ready
    db.refresh(job)
    db.refresh(doc)
    assert job.status == JobStatus.COMPLETED
    assert doc.status == DocumentStatus.READY
    assert doc.page_count == 1

    # Verify chunks inserted into database
    chunks = db.scalars(
        select(DocumentChunk).where(DocumentChunk.document_id == doc_id)
    ).all()
    assert len(chunks) >= 1
    assert any("DocuMind AI" in c.content for c in chunks)
    assert all(c.owner_id == user_id for c in chunks)
    assert all(c.workspace_id == ws_id for c in chunks)

    # Clean up storage
    storage.delete_file(storage_path)
    db.close()
