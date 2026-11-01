import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.models.workspace import Workspace
from app.models.document import Document
from app.models.chat import Conversation
from app.core.security import create_test_token

# Test database setup using SQLite in-memory with StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

TEST_TABLES = [Workspace.__table__, Document.__table__, Conversation.__table__]


@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh tables for every test."""
    Base.metadata.create_all(test_engine, tables=TEST_TABLES)
    yield
    Base.metadata.drop_all(test_engine, tables=TEST_TABLES)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_workspace_unauthenticated():
    response = client.post("/api/v1/workspaces", json={"name": "My Workspace"})
    assert response.status_code == 401


def test_create_and_get_workspace():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id, email="alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create workspace
    create_res = client.post(
        "/api/v1/workspaces",
        json={"name": "Research Project"},
        headers=headers,
    )
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["name"] == "Research Project"
    assert created_data["owner_id"] == str(user_id)
    workspace_id = created_data["id"]

    # Get workspace by ID
    get_res = client.get(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == workspace_id
    assert get_res.json()["name"] == "Research Project"


def test_list_workspaces_isolation():
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    token_a = create_test_token(user_id=user_a, email="user_a@example.com")
    token_b = create_test_token(user_id=user_b, email="user_b@example.com")

    # Create 2 workspaces for User A
    client.post("/api/v1/workspaces", json={"name": "A-WS-1"}, headers={"Authorization": f"Bearer {token_a}"})
    client.post("/api/v1/workspaces", json={"name": "A-WS-2"}, headers={"Authorization": f"Bearer {token_a}"})

    # Create 1 workspace for User B
    client.post("/api/v1/workspaces", json={"name": "B-WS-1"}, headers={"Authorization": f"Bearer {token_b}"})

    # User A list
    res_a = client.get("/api/v1/workspaces", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    items_a = res_a.json()
    assert len(items_a) == 2
    assert all(item["owner_id"] == str(user_a) for item in items_a)

    # User B list
    res_b = client.get("/api/v1/workspaces", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    items_b = res_b.json()
    assert len(items_b) == 1
    assert items_b[0]["owner_id"] == str(user_b)
    assert items_b[0]["name"] == "B-WS-1"


def test_cross_user_workspace_access_denied():
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    token_a = create_test_token(user_id=user_a)
    token_b = create_test_token(user_id=user_b)

    # User A creates a workspace
    create_res = client.post(
        "/api/v1/workspaces",
        json={"name": "Confidential Workspace"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert create_res.status_code == 201
    workspace_id = create_res.json()["id"]

    # User B attempts to access User A's workspace
    get_res = client.get(
        f"/api/v1/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert get_res.status_code == 404

    # User B attempts to update User A's workspace
    patch_res = client.patch(
        f"/api/v1/workspaces/{workspace_id}",
        json={"name": "Hacked Name"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert patch_res.status_code == 404

    # User B attempts to delete User A's workspace
    delete_res = client.delete(
        f"/api/v1/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert delete_res.status_code == 404

    # Verify workspace was not changed
    verify_res = client.get(
        f"/api/v1/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["name"] == "Confidential Workspace"


def test_update_and_delete_workspace():
    user_id = uuid.uuid4()
    token = create_test_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/v1/workspaces", json={"name": "Original Name"}, headers=headers)
    workspace_id = create_res.json()["id"]

    # Update name
    patch_res = client.patch(
        f"/api/v1/workspaces/{workspace_id}",
        json={"name": "Renamed Workspace"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Renamed Workspace"

    # Delete workspace
    del_res = client.delete(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    assert del_res.status_code == 204

    # Subsequent GET returns 404
    get_res = client.get(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    assert get_res.status_code == 404
