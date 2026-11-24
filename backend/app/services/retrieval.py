import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.services import embedding as embedding_service


def search_relevant_chunks(
    db: Session,
    owner_id: uuid.UUID,
    workspace_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.1,
    document_id: Optional[uuid.UUID] = None,
) -> List[Dict[str, Any]]:
    """Retrieve top-k relevant document chunks scoped strictly to the authenticated owner."""
    query_vector = embedding_service.get_embedding(query)

    is_postgres = db.bind is not None and db.bind.dialect.name == "postgresql"

    conditions = [
        DocumentChunk.owner_id == owner_id,
        DocumentChunk.workspace_id == workspace_id,
    ]
    if document_id:
        conditions.append(DocumentChunk.document_id == document_id)

    results: List[Dict[str, Any]] = []

    if is_postgres:
        # Use native PostgreSQL pgvector cosine distance operator (<=>)
        stmt = (
            select(
                DocumentChunk,
                Document.original_filename,
                DocumentChunk.embedding.cosine_distance(query_vector).label("distance"),
            )
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(*conditions)
            .order_by("distance")
            .limit(top_k)
        )
        for chunk, filename, distance in db.execute(stmt).all():
            similarity = 1.0 - float(distance) if distance is not None else 0.0
            if similarity >= similarity_threshold:
                results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_name": filename,
                    "page_number": chunk.page_number,
                    "content": chunk.content,
                    "similarity": similarity,
                })
    else:
        # In-memory cosine similarity for SQLite testing
        stmt = (
            select(DocumentChunk, Document.original_filename)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(*conditions)
        )
        scored_chunks = []
        for chunk, filename in db.execute(stmt).all():
            chunk_vec = list(chunk.embedding) if chunk.embedding is not None else []
            sim = embedding_service.cosine_similarity(query_vector, chunk_vec) if chunk_vec else 0.0
            scored_chunks.append((sim, chunk, filename))

        # Sort by similarity descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        for sim, chunk, filename in scored_chunks[:top_k]:
            if sim >= similarity_threshold:
                results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_name": filename,
                    "page_number": chunk.page_number,
                    "content": chunk.content,
                    "similarity": sim,
                })

    return results
