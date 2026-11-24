import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, AuthenticatedUser
from app.db.session import get_db
from app.schemas.job import JobResponse
from app.services import queue as queue_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobResponse:
    """Retrieve status of an ingestion job for the owner."""
    job = queue_service.get_job(db=db, owner_id=current_user.id, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or unauthorized.",
        )
    return JobResponse.model_validate(job)
