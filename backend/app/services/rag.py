import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.workspace import Workspace
from app.schemas.chat import AnswerResponse, CitationResponse
from app.services import retrieval, llm


def answer_question(
    db: Session,
    owner_id: uuid.UUID,
    workspace_id: uuid.UUID,
    question: str,
    document_id: Optional[uuid.UUID] = None,
) -> AnswerResponse:
    """Retrieve authorized document excerpts, apply relevance gate, and generate citation-backed answer."""
    # Verify workspace ownership
    workspace = db.scalar(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == owner_id,
        )
    )
    if not workspace:
        return AnswerResponse(
            question=question,
            answer="Workspace not found or unauthorized.",
            citations=[],
            has_sufficient_context=False,
        )

    # 1. Search relevant document chunks with evidence threshold
    chunks = retrieval.search_relevant_chunks(
        db=db,
        owner_id=owner_id,
        workspace_id=workspace_id,
        query=question,
        top_k=5,
        similarity_threshold=0.45,
        document_id=document_id,
    )

    # 2. Relevance Gate
    if not chunks:
        return AnswerResponse(
            question=question,
            answer="Based on the uploaded documents, there is insufficient evidence to answer this question.",
            citations=[],
            has_sufficient_context=False,
        )

    # 3. Generate grounded answer
    answer_text, has_context = llm.generate_llm_response(question, chunks)

    # 4. Map and validate citations
    citations = [
        CitationResponse(
            chunk_id=c["chunk_id"],
            document_id=c["document_id"],
            document_name=c["document_name"],
            page_number=c.get("page_number"),
            excerpt=c["content"][:200] + ("..." if len(c["content"]) > 200 else ""),
        )
        for c in chunks[:3]
    ]

    return AnswerResponse(
        question=question,
        answer=answer_text,
        citations=citations,
        has_sufficient_context=has_context,
    )
