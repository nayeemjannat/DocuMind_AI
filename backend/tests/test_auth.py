import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_test_token

client = TestClient(app)


def test_missing_token_returns_401():
    """Unauthenticated request must be rejected with 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "Missing or invalid Authorization header" in response.json()["detail"]


def test_invalid_token_returns_401():
    """Malformed token must be rejected with 401."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-jwt-token"}
    )
    assert response.status_code == 401
    assert "Invalid authentication token" in response.json()["detail"]


def test_wrong_secret_token_returns_401():
    """Token signed with an untrusted secret must be rejected."""
    user_id = uuid.uuid4()
    tampered_token = create_test_token(
        user_id=user_id,
        secret="wrong-secret-key-that-is-at-least-32-chars-long"
    )
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tampered_token}"}
    )
    assert response.status_code == 401
    assert "Invalid authentication token" in response.json()["detail"]


def test_expired_token_returns_401():
    """Expired token must be rejected with 401."""
    user_id = uuid.uuid4()
    expired_token = create_test_token(user_id=user_id, expires_in_minutes=-10)
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "Authentication token has expired" in response.json()["detail"]


def test_valid_token_returns_user():
    """Valid signed token must be accepted and return the user identity."""
    user_id = uuid.uuid4()
    valid_token = create_test_token(user_id=user_id, email="alice@example.com")
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["email"] == "alice@example.com"
    assert data["role"] == "authenticated"
