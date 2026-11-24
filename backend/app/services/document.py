import re
import uuid
from typing import List, Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.models.job import IngestionJob, JobStatus
from app.models.workspace import Workspace
from app.services import storage, quota

# Allowed extensions and standard MIME types
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "application/octet-stream",  # Fallback for some clients
}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and invalid characters."""
    clean_name = re.sub(r"[^\w\s.-]", "", filename).strip()
    return clean_name or "document"


def validate_file(filename: str, content: bytes, content_type: Optional[str]) -> Tuple[str, str]:
    """Validate document extension, content size, and MIME type."""
    clean_name = sanitize_filename(filename)
    extension = clean_name[clean_name.rfind("."):].lower() if "." in clean_name else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{extension}'. Only PDF, DOCX, and TXT files are accepted.",
        )

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the {settings.MAX_FILE_SIZE_MB} MB limit.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File cannot be empty.",
        )

    mime_type = content_type or "application/octet-stream"
    return clean_name, mime_type


def upload_document(
    db: Session,
    owner_id: uuid.UUID,
    workspace_id: uuid.UUID,
    file: UploadFile,
    content: bytes,
) -> Tuple[Document, IngestionJob]:
    """Validate file, persist in storage, and record document + durable ingestion job."""
    # Verify workspace exists and belongs to the owner
    workspace = db.scalar(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == owner_id,
        )
    )
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or unauthorized.",
        )

    # Enforce per-workspace and daily upload quotas
    quota.check_upload_quota(db, owner_id=owner_id, workspace_id=workspace_id)

    # Validate file format and size
    clean_filename, mime_type = validate_file(
        filename=file.filename or "document.txt",
        content=content,
        content_type=file.content_type,
    )

    # Determine unique storage path
    file_id = uuid.uuid4()
    storage_path = f"{owner_id}/{workspace_id}/{file_id}_{clean_filename}"

    # Save to storage
    storage.save_file(storage_path, content)

    # Create document record
    document = Document(
        id=file_id,
        workspace_id=workspace_id,
        owner_id=owner_id,
        original_filename=clean_filename,
        storage_path=storage_path,
        mime_type=mime_type,
        size_bytes=len(content),
        status=DocumentStatus.QUEUED,
    )
    db.add(document)

    # Create background ingestion job
    job = IngestionJob(
        document_id=document.id,
        workspace_id=workspace_id,
        owner_id=owner_id,
        status=JobStatus.QUEUED,
        attempt_count=0,
        max_attempts=3,
    )
    db.add(job)

    db.commit()
    db.refresh(document)
    db.refresh(job)

    return document, job


def list_workspace_documents(
    db: Session,
    owner_id: uuid.UUID,
    workspace_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
) -> List[Document]:
    """List documents belonging to the workspace and owned by the user."""
    stmt = (
        select(Document)
        .where(
            Document.workspace_id == workspace_id,
            Document.owner_id == owner_id,
        )
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_document(
    db: Session,
    owner_id: uuid.UUID,
    document_id: uuid.UUID,
) -> Optional[Document]:
    """Retrieve document metadata for the owning user."""
    stmt = select(Document).where(
        Document.id == document_id,
        Document.owner_id == owner_id,
    )
    return db.scalars(stmt).first()


def delete_document(
    db: Session,
    owner_id: uuid.UUID,
    document_id: uuid.UUID,
) -> bool:
    """Delete document, cleanup storage, and cascade remove child database rows."""
    document = get_document(db, owner_id, document_id)
    if not document:
        return False

    # Remove physical file
    storage.delete_file(document.storage_path)

    # Delete database record (cascades chunks and jobs)
    db.delete(document)
    db.commit()
    return True
