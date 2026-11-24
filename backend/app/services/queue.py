import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_

from app.models.job import IngestionJob, JobStatus
from app.models.document import Document, DocumentStatus


def claim_next_job(
    db: Session,
    worker_id: str,
    lease_seconds: int = 60,
) -> Optional[IngestionJob]:
    """Claim a queued or expired-lease job atomically with optimistic concurrency."""
    now = datetime.now(timezone.utc)
    lease_expiry = now + timedelta(seconds=lease_seconds)

    # Find jobs that are queued or have expired leases and haven't exceeded attempts
    stmt = (
        select(IngestionJob)
        .where(
            and_(
                IngestionJob.attempt_count < IngestionJob.max_attempts,
                or_(
                    IngestionJob.status == JobStatus.QUEUED,
                    and_(
                        IngestionJob.status == JobStatus.PROCESSING,
                        IngestionJob.lease_expires_at < now,
                    ),
                ),
            )
        )
        .order_by(IngestionJob.created_at.asc())
        .with_for_update(skip_locked=True)
    )

    job = db.scalars(stmt).first()
    if not job:
        return None

    # Update lease and attempt count
    job.status = JobStatus.PROCESSING
    job.worker_id = worker_id
    job.locked_at = now
    job.lease_expires_at = lease_expiry
    job.attempt_count += 1

    # Update document status to processing
    document = db.scalar(select(Document).where(Document.id == job.document_id))
    if document:
        document.status = DocumentStatus.PROCESSING

    db.commit()
    db.refresh(job)
    return job


def mark_job_completed(db: Session, job_id: uuid.UUID) -> bool:
    """Mark an ingestion job completed and set document status to ready."""
    job = db.scalar(select(IngestionJob).where(IngestionJob.id == job_id))
    if not job:
        return False

    now = datetime.now(timezone.utc)
    job.status = JobStatus.COMPLETED
    job.finished_at = now
    job.lease_expires_at = None

    document = db.scalar(select(Document).where(Document.id == job.document_id))
    if document:
        document.status = DocumentStatus.READY

    db.commit()
    return True


def mark_job_failed(db: Session, job_id: uuid.UUID, error_message: str) -> bool:
    """Record an error for the job; mark as permanently failed if max attempts reached."""
    job = db.scalar(select(IngestionJob).where(IngestionJob.id == job_id))
    if not job:
        return False

    job.last_error = error_message[:1000]

    document = db.scalar(select(Document).where(Document.id == job.document_id))

    if job.attempt_count >= job.max_attempts:
        job.status = JobStatus.FAILED
        job.finished_at = datetime.now(timezone.utc)
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = error_message[:1000]
    else:
        # Re-queue for next retry
        job.status = JobStatus.QUEUED
        job.worker_id = None
        job.lease_expires_at = None
        if document:
            document.status = DocumentStatus.QUEUED

    db.commit()
    return True


def get_job(db: Session, owner_id: uuid.UUID, job_id: uuid.UUID) -> Optional[IngestionJob]:
    """Retrieve an ingestion job owned by the user."""
    stmt = select(IngestionJob).where(
        IngestionJob.id == job_id,
        IngestionJob.owner_id == owner_id,
    )
    return db.scalars(stmt).first()
