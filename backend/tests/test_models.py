import uuid
from app.models import (
    Workspace,
    Document,
    DocumentStatus,
    DocumentChunk,
    IngestionJob,
    JobStatus,
    Conversation,
    Message,
    MessageRole,
)


def test_workspace_instantiation():
    owner_id = uuid.uuid4()
    ws = Workspace(name="Research", owner_id=owner_id)
    assert ws.name == "Research"
    assert ws.owner_id == owner_id
    assert ws.__tablename__ == "workspaces"


def test_document_instantiation():
    owner_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    doc = Document(
        workspace_id=ws_id,
        owner_id=owner_id,
        original_filename="paper.pdf",
        storage_path=f"{owner_id}/{ws_id}/paper.pdf",
        mime_type="application/pdf",
        size_bytes=1024 * 50,
        page_count=5,
        status=DocumentStatus.QUEUED,
    )
    assert doc.original_filename == "paper.pdf"
    assert doc.status == DocumentStatus.QUEUED
    assert doc.page_count == 5


def test_chunk_instantiation():
    owner_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    chunk = DocumentChunk(
        document_id=doc_id,
        workspace_id=ws_id,
        owner_id=owner_id,
        chunk_index=0,
        content="This is extracted text.",
        page_number=1,
    )
    assert chunk.chunk_index == 0
    assert chunk.content == "This is extracted text."
    assert chunk.page_number == 1


def test_job_instantiation():
    owner_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    job = IngestionJob(
        document_id=doc_id,
        workspace_id=ws_id,
        owner_id=owner_id,
        status=JobStatus.QUEUED,
        attempt_count=0,
        max_attempts=3,
    )
    assert job.status == JobStatus.QUEUED
    assert job.max_attempts == 3


def test_conversation_and_message_instantiation():
    owner_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    conv = Conversation(workspace_id=ws_id, owner_id=owner_id, title="Q&A Session")
    assert conv.title == "Q&A Session"

    msg = Message(
        conversation_id=uuid.uuid4(),
        workspace_id=ws_id,
        owner_id=owner_id,
        role=MessageRole.USER,
        content="What is the revenue?",
    )
    assert msg.role == MessageRole.USER
    assert msg.content == "What is the revenue?"
