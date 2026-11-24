import io
import os
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_test_token
from app.models.chunk import DocumentChunk
from app.models.chat import Conversation, Message
from app.models.document import Document
from app.services import ingestion, queue, storage
from tests.conftest import TestingSessionLocal

client = TestClient(app)


def test_conversation_crud_and_message_history():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create workspace and upload + ingest a document
    ws_res = client.post("/api/v1/workspaces", json={"name": "History Test WS"}, headers=headers)
    assert ws_res.status_code == 201
    workspace_id = ws_res.json()["id"]

    doc_content = (
        b"Project Orion launch date was November 2026 with a budget of 15 million USD."
    )
    files = {"file": ("orion_brief.txt", io.BytesIO(doc_content), "text/plain")}
    upload_res = client.post(f"/api/v1/workspaces/{workspace_id}/documents", files=files, headers=headers)
    assert upload_res.status_code == 201

    db = TestingSessionLocal()
    job = queue.claim_next_job(db, worker_id="test-worker")
    assert job is not None
    ingestion.process_ingestion_job(db, job)
    db.close()

    # 2. Create conversation
    conv_res = client.post(
        f"/api/v1/workspaces/{workspace_id}/conversations",
        json={},
        headers=headers,
    )
    assert conv_res.status_code == 201
    conv_data = conv_res.json()
    conv_id = conv_data["id"]
    assert conv_data["title"] == "New Conversation"

    # 3. Post a question in conversation
    msg_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"question": "What was the Project Orion launch date and budget?"},
        headers=headers,
    )
    assert msg_res.status_code == 200
    answer_data = msg_res.json()
    assert answer_data["has_sufficient_context"] is True
    assert "November 2026" in answer_data["answer"]
    assert answer_data["conversation_id"] == conv_id
    assert answer_data["message_id"] is not None
    assert len(answer_data["citations"]) > 0

    # 4. Verify auto-title and message history persistence
    get_conv = client.get(f"/api/v1/conversations/{conv_id}", headers=headers)
    assert get_conv.status_code == 200
    assert get_conv.json()["title"].startswith("What was the Project Orion launch date")

    hist_res = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers)
    assert hist_res.status_code == 200
    messages = hist_res.json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What was the Project Orion launch date and budget?"
    assert messages[1]["role"] == "assistant"
    assert "November 2026" in messages[1]["content"]
    assert len(messages[1]["citations"]) > 0
    assert messages[1]["citations"][0]["document_name"] == "orion_brief.txt"

    # 5. Rename and list conversations
    patch_res = client.patch(
        f"/api/v1/conversations/{conv_id}",
        json={"title": "Orion Launch Q&A"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Orion Launch Q&A"

    list_res = client.get(f"/api/v1/workspaces/{workspace_id}/conversations", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["title"] == "Orion Launch Q&A"


def test_ask_endpoint_with_conversation_id():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    ws_res = client.post("/api/v1/workspaces", json={"name": "Ask History WS"}, headers=headers)
    workspace_id = ws_res.json()["id"]

    conv_res = client.post(
        f"/api/v1/workspaces/{workspace_id}/conversations",
        json={"title": "Custom Chat"},
        headers=headers,
    )
    conv_id = conv_res.json()["id"]

    ask_res = client.post(
        f"/api/v1/workspaces/{workspace_id}/ask",
        json={"question": "What is the secret code?", "conversation_id": conv_id},
        headers=headers,
    )
    assert ask_res.status_code == 200
    assert ask_res.json()["conversation_id"] == conv_id
    assert ask_res.json()["has_sufficient_context"] is False

    hist_res = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers)
    assert hist_res.status_code == 200
    assert len(hist_res.json()) == 2


def test_conversation_cross_user_isolation():
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    headers_a = {"Authorization": f"Bearer {create_test_token(user_id=user_a)}"}
    headers_b = {"Authorization": f"Bearer {create_test_token(user_id=user_b)}"}

    ws_res = client.post("/api/v1/workspaces", json={"name": "Private WS"}, headers=headers_a)
    workspace_id = ws_res.json()["id"]

    conv_res = client.post(
        f"/api/v1/workspaces/{workspace_id}/conversations",
        json={"title": "Secret Chat"},
        headers=headers_a,
    )
    conv_id = conv_res.json()["id"]

    # User B cannot access, list, update, delete, or post to User A's conversation
    assert client.post(f"/api/v1/workspaces/{workspace_id}/conversations", json={}, headers=headers_b).status_code == 404
    assert client.get(f"/api/v1/workspaces/{workspace_id}/conversations", headers=headers_b).json() == []
    assert client.get(f"/api/v1/conversations/{conv_id}", headers=headers_b).status_code == 404
    assert client.patch(f"/api/v1/conversations/{conv_id}", json={"title": "Hacked"}, headers=headers_b).status_code == 404
    assert client.delete(f"/api/v1/conversations/{conv_id}", headers=headers_b).status_code == 404
    assert client.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers_b).status_code == 404
    assert client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"question": "Any secrets?"},
        headers=headers_b,
    ).status_code == 404


def test_cascade_deletion_and_storage_cleanup():
    user_id = uuid.uuid4()
    headers = {"Authorization": f"Bearer {create_test_token(user_id=user_id)}"}

    # Create workspace, upload 2 documents, ingest them, create conversation with messages
    ws_res = client.post("/api/v1/workspaces", json={"name": "Cleanup WS"}, headers=headers)
    workspace_id = ws_res.json()["id"]

    upload_1 = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files={"file": ("doc1.txt", io.BytesIO(b"First document text for cleanup testing."), "text/plain")},
        headers=headers,
    )
    doc1_id = upload_1.json()["document"]["id"]

    upload_2 = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files={"file": ("doc2.txt", io.BytesIO(b"Second document text for workspace cascade."), "text/plain")},
        headers=headers,
    )
    doc2_id = upload_2.json()["document"]["id"]

    db = TestingSessionLocal()
    for _ in range(2):
        job = queue.claim_next_job(db, worker_id="test-worker")
        assert job is not None
        ingestion.process_ingestion_job(db, job)

    doc1_row = db.get(Document, uuid.UUID(doc1_id))
    doc2_row = db.get(Document, uuid.UUID(doc2_id))
    doc1_storage_path = doc1_row.storage_path
    doc2_storage_path = doc2_row.storage_path
    assert storage.read_file(doc1_storage_path) is not None
    assert storage.read_file(doc2_storage_path) is not None
    db.close()

    conv_res = client.post(f"/api/v1/workspaces/{workspace_id}/conversations", json={}, headers=headers)
    conv_id = conv_res.json()["id"]
    client.post(f"/api/v1/conversations/{conv_id}/messages", json={"question": "First document?"}, headers=headers)

    # 1. Delete single document -> removes physical file and derived chunks
    del_doc = client.delete(f"/api/v1/documents/{doc1_id}", headers=headers)
    assert del_doc.status_code == 204
    assert storage.read_file(doc1_storage_path) is None

    db = TestingSessionLocal()
    assert db.query(DocumentChunk).filter(DocumentChunk.document_id == uuid.UUID(doc1_id)).count() == 0
    db.close()

    # 2. Delete conversation -> removes messages
    del_conv = client.delete(f"/api/v1/conversations/{conv_id}", headers=headers)
    assert del_conv.status_code == 204

    db = TestingSessionLocal()
    assert db.query(Message).filter(Message.conversation_id == uuid.UUID(conv_id)).count() == 0
    db.close()

    # 3. Create another conversation, then delete entire workspace -> removes remaining physical files & DB rows
    conv2_res = client.post(f"/api/v1/workspaces/{workspace_id}/conversations", json={}, headers=headers)
    conv2_id = conv2_res.json()["id"]
    client.post(f"/api/v1/conversations/{conv2_id}/messages", json={"question": "Second document?"}, headers=headers)

    del_ws = client.delete(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    assert del_ws.status_code == 204
    assert storage.read_file(doc2_storage_path) is None

    db = TestingSessionLocal()
    assert db.query(Document).filter(Document.workspace_id == uuid.UUID(workspace_id)).count() == 0
    assert db.query(DocumentChunk).filter(DocumentChunk.workspace_id == uuid.UUID(workspace_id)).count() == 0
    assert db.query(Conversation).filter(Conversation.workspace_id == uuid.UUID(workspace_id)).count() == 0
    assert db.query(Message).filter(Message.workspace_id == uuid.UUID(workspace_id)).count() == 0
    db.close()
