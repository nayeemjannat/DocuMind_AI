import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000, description="Question text to answer from documents")
    document_id: Optional[uuid.UUID] = Field(None, description="Optional document filter")


class CitationResponse(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    page_number: Optional[int] = None
    excerpt: str


class AnswerResponse(BaseModel):
    question: str
    answer: str
    citations: List[CitationResponse]
    has_sufficient_context: bool
