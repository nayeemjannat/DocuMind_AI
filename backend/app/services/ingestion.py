import logging
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.job import IngestionJob
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.services import storage, parser, chunker, queue, embedding as embedding_service

logger = logging.getLogger(__name__)


def process_ingestion_job(db: Session, job: IngestionJob) -> bool:
    """Execute text extraction, chunking, and persistence for a claimed job."""
    try:
        document = db.scalar(select(Document).where(Document.id == job.document_id))
        if not document:
            raise ValueError(f"Document {job.document_id} not found.")

        # Read binary file from private storage
        content = storage.read_file(document.storage_path)
        if not content:
            raise ValueError(f"Storage object {document.storage_path} not found.")

        # Parse text page by page
        pages = parser.parse_document(document.original_filename, content)
        if not pages:
            raise ValueError("No extractable text found in document.")

        document.page_count = len(pages)

        # Break text into overlapping chunks
        chunks_data = chunker.chunk_document_pages(pages)
        if not chunks_data:
            raise ValueError("Failed to generate document chunks.")

        # Delete any existing chunks for this document (idempotency on retry)
        existing_chunks = db.scalars(
            select(DocumentChunk).where(DocumentChunk.document_id == document.id)
        ).all()
        for chunk in existing_chunks:
            db.delete(chunk)

        # Insert new chunks
        for item in chunks_data:
            vec = embedding_service.get_embedding(item["content"])
            chunk = DocumentChunk(
                document_id=document.id,
                workspace_id=document.workspace_id,
                owner_id=document.owner_id,
                chunk_index=item["chunk_index"],
                content=item["content"],
                page_number=item["page_number"],
                metadata_=item["metadata"],
                embedding=vec,
            )
            db.add(chunk)

        db.commit()

        # Mark job completed and document ready
        queue.mark_job_completed(db, job.id)
        return True

    except Exception as e:
        logger.exception("Error processing ingestion job %s", job.id)
        db.rollback()
        queue.mark_job_failed(db, job.id, str(e))
        return False
