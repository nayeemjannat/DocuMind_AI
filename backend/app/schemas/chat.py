import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.chat import MessageRole


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000, description="Question text to answer from documents")
    document_id: Optional[uuid.UUID] = Field(None, description="Optional document filter")
    conversation_id: Optional[uuid.UUID] = Field(None, description="Optional conversation ID to append message to history")


class CitationResponse(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    page_number: Optional[int] = None
    excerpt: str

    model_config = ConfigDict(from_attributes=True)


class AnswerResponse(BaseModel):
    question: str
    answer: str
    citations: List[CitationResponse] = []
    has_sufficient_context: bool = True
    conversation_id: Optional[uuid.UUID] = None
    message_id: Optional[uuid.UUID] = None


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Optional initial conversation title")


class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Updated conversation title")


class ConversationResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    owner_id: uuid.UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    workspace_id: uuid.UUID
    owner_id: uuid.UUID
    role: MessageRole
    content: str
    citations: List[CitationResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
