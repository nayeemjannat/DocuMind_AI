import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, AuthenticatedUser
from app.db.session import get_db
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services import document as document_service

router = APIRouter(tags=["documents"])


@router.post(
    "/workspaces/{workspace_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    workspace_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    """Upload a document to an owned workspace, validate format/size, and queue ingestion."""
    content = await file.read()
    document, job = document_service.upload_document(
        db=db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
        file=file,
        content=content,
    )
    return DocumentUploadResponse(
        document=DocumentResponse.model_validate(document),
        job_id=job.id,
        job_status=job.status.value,
    )


@router.get(
    "/workspaces/{workspace_id}/documents",
    response_model=List[DocumentResponse],
)
def list_documents(
    workspace_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentResponse]:
    """List documents in an owned workspace."""
    documents = document_service.list_workspace_documents(
        db=db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
        limit=limit,
        offset=offset,
    )
    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """Retrieve document metadata for the owner."""
    document = document_service.get_document(
        db=db,
        owner_id=current_user.id,
        document_id=document_id,
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or unauthorized.",
        )
    return DocumentResponse.model_validate(document)


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a document and its storage file."""
    deleted = document_service.delete_document(
        db=db,
        owner_id=current_user.id,
        document_id=document_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or unauthorized.",
        )
