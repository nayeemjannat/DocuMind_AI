import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, AuthenticatedUser
from app.db.session import get_db
from app.schemas.chat import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageResponse,
    QuestionRequest,
    AnswerResponse,
)
from app.services import conversation as conversation_service

router = APIRouter(tags=["conversations"])


@router.post(
    "/workspaces/{workspace_id}/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    workspace_id: uuid.UUID,
    data: ConversationCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Create a new chat conversation session in an owned workspace."""
    conversation = conversation_service.create_conversation(
        db=db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
        title=data.title,
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or unauthorized.",
        )
    return ConversationResponse.model_validate(conversation)


@router.get(
    "/workspaces/{workspace_id}/conversations",
    response_model=List[ConversationResponse],
    status_code=status.HTTP_200_OK,
)
def list_conversations(
    workspace_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ConversationResponse]:
    """List conversation sessions in an owned workspace."""
    conversations = conversation_service.list_conversations(
        db=db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
        limit=limit,
        offset=offset,
    )
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
)
def get_conversation(
    conversation_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Retrieve an owned conversation by ID."""
    conversation = conversation_service.get_conversation(
        db=db,
        owner_id=current_user.id,
        conversation_id=conversation_id,
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or unauthorized.",
        )
    return ConversationResponse.model_validate(conversation)


@router.patch(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
)
def update_conversation(
    conversation_id: uuid.UUID,
    data: ConversationUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Update conversation title."""
    conversation = conversation_service.update_conversation(
        db=db,
        owner_id=current_user.id,
        conversation_id=conversation_id,
        title=data.title,
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or unauthorized.",
        )
    return ConversationResponse.model_validate(conversation)


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a conversation and cascade remove its messages."""
    deleted = conversation_service.delete_conversation(
        db=db,
        owner_id=current_user.id,
        conversation_id=conversation_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or unauthorized.",
        )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[MessageResponse],
    status_code=status.HTTP_200_OK,
)
def list_messages(
    conversation_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[MessageResponse]:
    """Retrieve message history for an owned conversation."""
    messages = conversation_service.list_messages(
        db=db,
        owner_id=current_user.id,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )
    if messages is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or unauthorized.",
        )
    return [MessageResponse.model_validate(m) for m in messages]


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=AnswerResponse,
    status_code=status.HTTP_200_OK,
)
def post_conversation_message(
    conversation_id: uuid.UUID,
    data: QuestionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnswerResponse:
    """Ask a question within a conversation and receive a grounded answer with citations."""
    result = conversation_service.post_conversation_message(
        db=db,
        owner_id=current_user.id,
        conversation_id=conversation_id,
        question=data.question,
        document_id=data.document_id,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or unauthorized.",
        )
    _, answer_res = result
    return answer_res
