import io
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_test_token
from app.services import ingestion, queue
from tests.conftest import TestingSessionLocal

client = TestClient(app)


def test_rag_grounded_answer_and_citations():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create workspace
    ws_res = client.post("/api/v1/workspaces", json={"name": "AI Research"}, headers=headers)
    assert ws_res.status_code == 201
    workspace_id = ws_res.json()["id"]

    # 2. Upload document containing specific facts
    doc_content = (
        b"DocuMind AI provides verifiable citations for every answer. "
        b"The annual revenue of TechCorp in 2025 was 42 million USD. "
        b"The CEO of TechCorp announced expansion into European markets."
    )
    files = {"file": ("techcorp_report.txt", io.BytesIO(doc_content), "text/plain")}
    upload_res = client.post(f"/api/v1/workspaces/{workspace_id}/documents", files=files, headers=headers)
    assert upload_res.status_code == 201

    # Process ingestion job
    db = TestingSessionLocal()
    job = queue.claim_next_job(db, worker_id="test-worker")
    assert job is not None
    ingestion.process_ingestion_job(db, job)
    db.close()

    # 3. Ask question directly answered by document
    ask_res = client.post(
        f"/api/v1/workspaces/{workspace_id}/ask",
        json={"question": "What was the revenue of TechCorp in 2025?"},
        headers=headers,
    )
    assert ask_res.status_code == 200
    data = ask_res.json()
    assert data["has_sufficient_context"] is True
    assert "42 million" in data["answer"]
    assert len(data["citations"]) > 0
    assert data["citations"][0]["document_name"] == "techcorp_report.txt"
    assert "42 million" in data["citations"][0]["excerpt"]


def test_rag_insufficient_evidence_gate():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    ws_res = client.post("/api/v1/workspaces", json={"name": "Astronomy"}, headers=headers)
    workspace_id = ws_res.json()["id"]

    # Upload document about space
    doc_content = b"The planet Mars has two small moons named Phobos and Deimos."
    files = {"file": ("mars.txt", io.BytesIO(doc_content), "text/plain")}
    upload_res = client.post(f"/api/v1/workspaces/{workspace_id}/documents", files=files, headers=headers)
    assert upload_res.status_code == 201

    # Ingest document
    db = TestingSessionLocal()
    job = queue.claim_next_job(db, worker_id="test-worker")
    ingestion.process_ingestion_job(db, job)
    db.close()

    # Ask completely unrelated question
    ask_res = client.post(
        f"/api/v1/workspaces/{workspace_id}/ask",
        json={"question": "What are the quarterly financial results of Apple?"},
        headers=headers,
    )
    assert ask_res.status_code == 200
    data = ask_res.json()
    assert data["has_sufficient_context"] is False
    assert "insufficient evidence" in data["answer"].lower()
    assert len(data["citations"]) == 0


def test_rag_cross_user_isolation():
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    token_a = create_test_token(user_id=user_a)
    token_b = create_test_token(user_id=user_b)

    # User A creates workspace and uploads secret document
    ws_res = client.post("/api/v1/workspaces", json={"name": "A-Secret-Space"}, headers={"Authorization": f"Bearer {token_a}"})
    workspace_a_id = ws_res.json()["id"]

    secret_content = b"The classified password for project X is SuperSecretPassword123."
    client.post(
        f"/api/v1/workspaces/{workspace_a_id}/documents",
        files={"file": ("secret.txt", io.BytesIO(secret_content), "text/plain")},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    db = TestingSessionLocal()
    job = queue.claim_next_job(db, worker_id="test-worker")
    ingestion.process_ingestion_job(db, job)
    db.close()

    # 1. User B tries to ask in User A's workspace -> 404
    ask_intruder = client.post(
        f"/api/v1/workspaces/{workspace_a_id}/ask",
        json={"question": "What is the password for project X?"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert ask_intruder.status_code == 404

    # 2. User B creates their own workspace and asks -> should not leak User A's document
    ws_b = client.post("/api/v1/workspaces", json={"name": "B-Space"}, headers={"Authorization": f"Bearer {token_b}"})
    workspace_b_id = ws_b.json()["id"]

    ask_b = client.post(
        f"/api/v1/workspaces/{workspace_b_id}/ask",
        json={"question": "What is the classified password for project X?"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert ask_b.status_code == 200
    assert "insufficient evidence" in ask_b.json()["answer"].lower()
    assert len(ask_b.json()["citations"]) == 0
