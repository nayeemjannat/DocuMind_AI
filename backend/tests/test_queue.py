import uuid
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models.job import IngestionJob, JobStatus
from app.models.document import Document, DocumentStatus
from app.models.workspace import Workspace
from app.core.security import create_test_token
from app.services import queue as queue_service
from tests.conftest import TestingSessionLocal

client = TestClient(app)


def test_claim_job_and_lease():
    db = TestingSessionLocal()
    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    ws = Workspace(id=ws_id, name="Q-Space", owner_id=user_id)
    doc = Document(
        id=uuid.uuid4(),
        workspace_id=ws_id,
        owner_id=user_id,
        original_filename="doc.txt",
        storage_path="path/doc.txt",
        mime_type="text/plain",
        size_bytes=100,
        status=DocumentStatus.QUEUED,
    )
    job = IngestionJob(
        id=uuid.uuid4(),
        document_id=doc.id,
        workspace_id=ws_id,
        owner_id=user_id,
        status=JobStatus.QUEUED,
        attempt_count=0,
        max_attempts=3,
    )
    db.add_all([ws, doc, job])
    db.commit()

    # Worker 1 claims job
    claimed = queue_service.claim_next_job(db, worker_id="worker-1", lease_seconds=30)
    assert claimed is not None
    assert claimed.id == job.id
    assert claimed.status == JobStatus.PROCESSING
    assert claimed.worker_id == "worker-1"
    assert claimed.attempt_count == 1
    assert claimed.lease_expires_at is not None

    # No second job available right now
    second_claim = queue_service.claim_next_job(db, worker_id="worker-2", lease_seconds=30)
    assert second_claim is None
    db.close()


def test_stale_lease_recovery():
    db = TestingSessionLocal()
    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    ws = Workspace(id=ws_id, name="Stale-Space", owner_id=user_id)
    doc = Document(
        id=uuid.uuid4(),
        workspace_id=ws_id,
        owner_id=user_id,
        original_filename="doc.txt",
        storage_path="path/doc.txt",
        mime_type="text/plain",
        size_bytes=100,
        status=DocumentStatus.PROCESSING,
    )
    # Stale job with expired lease in the past
    past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    job = IngestionJob(
        id=uuid.uuid4(),
        document_id=doc.id,
        workspace_id=ws_id,
        owner_id=user_id,
        status=JobStatus.PROCESSING,
        worker_id="crashed-worker",
        lease_expires_at=past_time,
        attempt_count=1,
        max_attempts=3,
    )
    db.add_all([ws, doc, job])
    db.commit()

    # New worker should recover the stale job
    recovered = queue_service.claim_next_job(db, worker_id="healthy-worker", lease_seconds=60)
    assert recovered is not None
    assert recovered.id == job.id
    assert recovered.worker_id == "healthy-worker"
    assert recovered.attempt_count == 2
    db.close()


def test_job_failure_retry_and_max_attempts():
    db = TestingSessionLocal()
    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    ws = Workspace(id=ws_id, name="Fail-Space", owner_id=user_id)
    doc = Document(
        id=uuid.uuid4(),
        workspace_id=ws_id,
        owner_id=user_id,
        original_filename="f.txt",
        storage_path="path/f.txt",
        mime_type="text/plain",
        size_bytes=10,
        status=DocumentStatus.PROCESSING,
    )
    job = IngestionJob(
        id=uuid.uuid4(),
        document_id=doc.id,
        workspace_id=ws_id,
        owner_id=user_id,
        status=JobStatus.PROCESSING,
        attempt_count=1,
        max_attempts=2,
    )
    db.add_all([ws, doc, job])
    db.commit()

    # First failure -> re-queues because attempt_count (1) < max_attempts (2)
    queue_service.mark_job_failed(db, job.id, "Temporary network error")
    db.refresh(job)
    assert job.status == JobStatus.QUEUED

    # Claim again
    claimed = queue_service.claim_next_job(db, worker_id="w-1")
    assert claimed.attempt_count == 2

    # Second failure -> marks permanently failed because attempt_count (2) >= max_attempts (2)
    queue_service.mark_job_failed(db, job.id, "Permanent corrupt file")
    db.refresh(job)
    assert job.status == JobStatus.FAILED
    assert job.last_error == "Permanent corrupt file"

    db.refresh(doc)
    assert doc.status == DocumentStatus.FAILED
    db.close()


def test_get_job_api_status_and_isolation():
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    token_a = create_test_token(user_id=user_a)
    token_b = create_test_token(user_id=user_b)

    db = TestingSessionLocal()
    ws_a = Workspace(id=uuid.uuid4(), name="Space-A", owner_id=user_a)
    doc_a = Document(
        id=uuid.uuid4(),
        workspace_id=ws_a.id,
        owner_id=user_a,
        original_filename="doc.txt",
        storage_path="path/doc.txt",
        mime_type="text/plain",
        size_bytes=50,
    )
    job_a = IngestionJob(
        id=uuid.uuid4(),
        document_id=doc_a.id,
        workspace_id=ws_a.id,
        owner_id=user_a,
        status=JobStatus.QUEUED,
    )
    db.add_all([ws_a, doc_a, job_a])
    db.commit()

    # User A gets 200 with job status
    res_a = client.get(f"/api/v1/jobs/{job_a.id}", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    assert res_a.json()["id"] == str(job_a.id)
    assert res_a.json()["status"] == "queued"

    # User B gets 404 (isolation)
    res_b = client.get(f"/api/v1/jobs/{job_a.id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 404
    db.close()
