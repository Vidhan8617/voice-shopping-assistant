"""
Integration tests hitting the actual API via FastAPI's TestClient
(in-memory, no real server needed). Uses a separate in-memory SQLite DB
so tests never touch the real shopping_assistant.db file.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"
# StaticPool makes every session share the SAME underlying connection.
# Without this, SQLite's :memory: gives each new connection its own blank
# database, so a session that created the tables and a session that later
# queries them would be looking at two different (dis)connected databases.
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_add_item_via_list_endpoint():
    response = client.post("/api/list", json={"name": "Milk", "quantity": 1})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "milk"
    assert data["category"] == "Dairy"


def test_get_list_returns_added_items():
    client.post("/api/list", json={"name": "bread"})
    response = client.get("/api/list")
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert "bread" in names


def test_voice_command_add():
    response = client.post("/api/voice/command", json={"transcript": "add milk", "language": "en"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"]["action"] == "add"
    assert data["item"]["name"] == "milk"


def test_voice_command_remove_nonexistent_item_does_not_crash():
    response = client.post("/api/voice/command", json={"transcript": "remove nonexistent_xyz", "language": "en"})
    assert response.status_code == 200
    assert "isn't on your list" in response.json()["message"]


def test_remove_item_by_id():
    add_response = client.post("/api/list", json={"name": "eggs"})
    item_id = add_response.json()["id"]
    delete_response = client.delete(f"/api/list/{item_id}")
    assert delete_response.status_code == 204


def test_remove_nonexistent_item_returns_404():
    response = client.delete("/api/list/99999")
    assert response.status_code == 404


def test_search_endpoint_requires_query_param():
    response = client.get("/api/search")
    assert response.status_code == 422  # missing required 'q' param
