import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, AuthenticatedUser
from app.db.session import get_db
from app.schemas.chat import QuestionRequest, AnswerResponse
from app.services import rag as rag_service

router = APIRouter(tags=["chat"])


@router.post(
    "/workspaces/{workspace_id}/ask",
    response_model=AnswerResponse,
    status_code=status.HTTP_200_OK,
)
def ask_document_question(
    workspace_id: uuid.UUID,
    data: QuestionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnswerResponse:
    """Ask a question about workspace documents and receive an answer with source citations."""
    response = rag_service.answer_question(
        db=db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
        question=data.question,
        document_id=data.document_id,
    )
    if response.answer == "Workspace not found or unauthorized.":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or unauthorized.",
        )
    return response
