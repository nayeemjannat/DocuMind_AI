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
from app.models.chunk import DocumentChunk
from app.models.job import IngestionJob
from app.models.chat import Conversation, Message
from app.services import quota

# Shared SQLite in-memory test database with StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

TEST_TABLES = [
    Workspace.__table__,
    Document.__table__,
    DocumentChunk.__table__,
    IngestionJob.__table__,
    Conversation.__table__,
    Message.__table__,
]


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def db_session():
    """Create fresh tables before every test and drop them after."""
    quota.reset_rate_limits()
    Base.metadata.create_all(test_engine, tables=TEST_TABLES)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(test_engine, tables=TEST_TABLES)
    quota.reset_rate_limits()


@pytest.fixture
def client():
    return TestClient(app)
