import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.chat import Conversation, Message, MessageRole
from app.models.workspace import Workspace
from app.schemas.chat import AnswerResponse
from app.services import rag as rag_service


def create_conversation(
    db: Session,
    owner_id: uuid.UUID,
    workspace_id: uuid.UUID,
    title: Optional[str] = None,
) -> Optional[Conversation]:
    """Create a new chat conversation in an owned workspace."""
    # Verify workspace exists and belongs to the owner
    workspace = db.scalar(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == owner_id,
        )
    )
    if not workspace:
        return None

    clean_title = title.strip() if title and title.strip() else "New Conversation"
    conversation = Conversation(
        workspace_id=workspace_id,
        owner_id=owner_id,
        title=clean_title,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(
    db: Session,
    owner_id: uuid.UUID,
    workspace_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
) -> List[Conversation]:
    """List conversations for an owned workspace ordered by latest update."""
    # Ensure workspace belongs to user
    workspace = db.scalar(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == owner_id,
        )
    )
    if not workspace:
        return []

    stmt = (
        select(Conversation)
        .where(
            Conversation.workspace_id == workspace_id,
            Conversation.owner_id == owner_id,
        )
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_conversation(
    db: Session,
    owner_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> Optional[Conversation]:
    """Retrieve an owned conversation by its ID."""
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.owner_id == owner_id,
    )
    return db.scalars(stmt).first()


def update_conversation(
    db: Session,
    owner_id: uuid.UUID,
    conversation_id: uuid.UUID,
    title: str,
) -> Optional[Conversation]:
    """Update conversation title."""
    conversation = get_conversation(db, owner_id, conversation_id)
    if not conversation:
        return None

    conversation.title = title.strip()
    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(
    db: Session,
    owner_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> bool:
    """Delete a conversation and cascade remove all its messages."""
    conversation = get_conversation(db, owner_id, conversation_id)
    if not conversation:
        return False

    db.delete(conversation)
    db.commit()
    return True


def list_messages(
    db: Session,
    owner_id: uuid.UUID,
    conversation_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
) -> Optional[List[Message]]:
    """List messages in an owned conversation ordered chronologically."""
    conversation = get_conversation(db, owner_id, conversation_id)
    if not conversation:
        return None

    stmt = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.owner_id == owner_id,
        )
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def post_conversation_message(
    db: Session,
    owner_id: uuid.UUID,
    conversation_id: uuid.UUID,
    question: str,
    document_id: Optional[uuid.UUID] = None,
) -> Optional[Tuple[Message, AnswerResponse]]:
    """Submit a question in a conversation, generate grounded answer, and persist both messages."""
    conversation = get_conversation(db, owner_id, conversation_id)
    if not conversation:
        return None

    # 1. Persist user message
    user_msg = Message(
        conversation_id=conversation.id,
        workspace_id=conversation.workspace_id,
        owner_id=owner_id,
        role=MessageRole.USER,
        content=question.strip(),
        citations=[],
    )
    db.add(user_msg)
    db.flush()

    # 2. Generate grounded answer via RAG
    answer_res = rag_service.answer_question(
        db=db,
        owner_id=owner_id,
        workspace_id=conversation.workspace_id,
        question=question,
        document_id=document_id,
    )

    # 3. Format citations for persistence
    citations_data: List[Dict[str, Any]] = [
        {
            "chunk_id": str(c.chunk_id),
            "document_id": str(c.document_id),
            "document_name": c.document_name,
            "page_number": c.page_number,
            "excerpt": c.excerpt,
        }
        for c in answer_res.citations
    ]

    # 4. Persist assistant response message
    assistant_msg = Message(
        conversation_id=conversation.id,
        workspace_id=conversation.workspace_id,
        owner_id=owner_id,
        role=MessageRole.ASSISTANT,
        content=answer_res.answer,
        citations=citations_data,
    )
    db.add(assistant_msg)

    # Auto-generate title if conversation has default title
    if conversation.title in ("New Conversation", None):
        snippet = question.strip()
        conversation.title = snippet[:40] + ("..." if len(snippet) > 40 else "")

    conversation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(assistant_msg)

    answer_res.conversation_id = conversation.id
    answer_res.message_id = assistant_msg.id
    return assistant_msg, answer_res
