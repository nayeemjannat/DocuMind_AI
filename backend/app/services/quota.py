import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Tuple
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.chat import Message, MessageRole
from app.models.document import Document

# Tracks stateless /ask calls that are not persisted to a conversation
_stateless_question_counts: Dict[Tuple[str, str], int] = defaultdict(int)


def reset_rate_limits() -> None:
    """Clear in-memory rate limit counters (used in tests)."""
    _stateless_question_counts.clear()


def _today_utc_start() -> datetime:
    now = datetime.now(timezone.utc)
    return datetime(now.year, now.month, now.day, tzinfo=timezone.utc)


def check_upload_quota(db: Session, owner_id: uuid.UUID, workspace_id: uuid.UUID) -> None:
    """Enforce per-workspace document limit and daily upload quota per account."""
    ws_doc_count = db.scalar(
        select(func.count(Document.id)).where(
            Document.workspace_id == workspace_id,
            Document.owner_id == owner_id,
        )
    ) or 0

    if ws_doc_count >= settings.MAX_DOCS_PER_WORKSPACE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "QUOTA_EXCEEDED",
                "message": f"Workspace document limit reached (max {settings.MAX_DOCS_PER_WORKSPACE} documents).",
            },
        )

    today_start = _today_utc_start()
    daily_uploads = db.scalar(
        select(func.count(Document.id)).where(
            Document.owner_id == owner_id,
            Document.created_at >= today_start,
        )
    ) or 0

    if daily_uploads >= settings.MAX_DAILY_UPLOADS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "QUOTA_EXCEEDED",
                "message": f"Daily upload limit reached (max {settings.MAX_DAILY_UPLOADS} uploads per day).",
            },
        )


def check_and_record_question_quota(
    db: Session,
    owner_id: uuid.UUID,
    persisted_in_conversation: bool = False,
) -> None:
    """Enforce daily question limit per account across both persisted and stateless endpoints."""
    today_start = _today_utc_start()
    today_key = today_start.strftime("%Y-%m-%d")

    persisted_count = db.scalar(
        select(func.count(Message.id)).where(
            Message.owner_id == owner_id,
            Message.role == MessageRole.USER,
            Message.created_at >= today_start,
        )
    ) or 0

    stateless_key = (str(owner_id), today_key)
    total_today = persisted_count + _stateless_question_counts[stateless_key]

    if total_today >= settings.MAX_DAILY_QUESTIONS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMITED",
                "message": f"Daily question limit reached (max {settings.MAX_DAILY_QUESTIONS} questions per day).",
            },
        )

    if not persisted_in_conversation:
        _stateless_question_counts[stateless_key] += 1
