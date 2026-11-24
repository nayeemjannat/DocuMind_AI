import io
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_test_token

client = TestClient(app)


def test_upload_valid_pdf_document():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # Create workspace first
    ws_res = client.post("/api/v1/workspaces", json={"name": "Doc Space"}, headers=headers)
    assert ws_res.status_code == 201
    workspace_id = ws_res.json()["id"]

    # Upload PDF
    pdf_content = b"%PDF-1.4 Mock PDF file content for testing"
    files = {"file": ("report.pdf", io.BytesIO(pdf_content), "application/pdf")}

    upload_res = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files=files,
        headers=headers,
    )
    assert upload_res.status_code == 201
    data = upload_res.json()
    assert data["document"]["original_filename"] == "report.pdf"
    assert data["document"]["size_bytes"] == len(pdf_content)
    assert data["document"]["status"] == "queued"
    assert data["job_status"] == "queued"
    assert "job_id" in data


def test_upload_valid_docx_and_txt():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    ws_res = client.post("/api/v1/workspaces", json={"name": "Multi Doc Space"}, headers=headers)
    workspace_id = ws_res.json()["id"]

    # Upload TXT
    txt_content = b"Simple text document content."
    res_txt = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files={"file": ("notes.txt", io.BytesIO(txt_content), "text/plain")},
        headers=headers,
    )
    assert res_txt.status_code == 201
    assert res_txt.json()["document"]["original_filename"] == "notes.txt"

    # Upload DOCX
    docx_content = b"PK\x03\x04 mock docx binary bytes"
    res_docx = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files={"file": ("summary.docx", io.BytesIO(docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers=headers,
    )
    assert res_docx.status_code == 201
    assert res_docx.json()["document"]["original_filename"] == "summary.docx"


def test_reject_unsupported_file_extension():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    ws_res = client.post("/api/v1/workspaces", json={"name": "Test Space"}, headers=headers)
    workspace_id = ws_res.json()["id"]

    # Upload unsupported .exe
    files = {"file": ("program.exe", io.BytesIO(b"binary data"), "application/octet-stream")}
    res = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files=files,
        headers=headers,
    )
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]


def test_reject_oversized_file():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    ws_res = client.post("/api/v1/workspaces", json={"name": "Size Test Space"}, headers=headers)
    workspace_id = ws_res.json()["id"]

    # Create file slightly exceeding 5 MB limit
    oversized_content = b"0" * (5 * 1024 * 1024 + 1024)
    files = {"file": ("huge.pdf", io.BytesIO(oversized_content), "application/pdf")}

    res = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files=files,
        headers=headers,
    )
    assert res.status_code == 400
    assert "exceeds" in res.json()["detail"]


def test_cross_user_document_isolation():
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    token_a = create_test_token(user_id=user_a)
    token_b = create_test_token(user_id=user_b)

    # User A creates workspace and uploads document
    ws_res = client.post("/api/v1/workspaces", json={"name": "A-Private"}, headers={"Authorization": f"Bearer {token_a}"})
    workspace_a_id = ws_res.json()["id"]

    upload_res = client.post(
        f"/api/v1/workspaces/{workspace_a_id}/documents",
        files={"file": ("secret.pdf", io.BytesIO(b"%PDF confidential"), "application/pdf")},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert upload_res.status_code == 201
    document_id = upload_res.json()["document"]["id"]

    # User B attempts to upload into User A's workspace
    b_upload = client.post(
        f"/api/v1/workspaces/{workspace_a_id}/documents",
        files={"file": ("intruder.pdf", io.BytesIO(b"%PDF intruder"), "application/pdf")},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert b_upload.status_code == 404

    # User B attempts to get User A's document
    b_get = client.get(
        f"/api/v1/documents/{document_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert b_get.status_code == 404

    # User B attempts to delete User A's document
    b_delete = client.delete(
        f"/api/v1/documents/{document_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert b_delete.status_code == 404

    # User A successfully gets and deletes the document
    a_get = client.get(
        f"/api/v1/documents/{document_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert a_get.status_code == 200

    a_delete = client.delete(
        f"/api/v1/documents/{document_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert a_delete.status_code == 204
