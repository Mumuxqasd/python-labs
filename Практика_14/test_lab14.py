import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import app, get_service
from database import Base
from repository import ServerRepository
from service import ServerService


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    def override_service():
        session = Session()
        try:
            yield ServerService(ServerRepository(session))
        finally:
            session.close()

    app.dependency_overrides[get_service] = override_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def data(name="srv", ip="10.0.0.1", cpu=20, status="online"):
    return {"hostname": name, "ip": ip, "os_name": "Linux", "cpu": cpu, "ram": 4096, "status": status}


def test_get_empty(client):
    assert client.get("/servers").json() == []


def test_post(client):
    assert client.post("/servers", json=data()).status_code == 201


def test_get_existing(client):
    client.post("/servers", json=data())
    assert client.get("/servers/1").status_code == 200


def test_get_missing(client):
    assert client.get("/servers/999").status_code == 404


def test_post_invalid(client):
    assert client.post("/servers", json=data(cpu=150)).status_code == 422


def test_put(client):
    client.post("/servers", json=data())
    assert client.put("/servers/1", json=data("new", "10.0.0.2", 30, "maintenance")).json()["hostname"] == "new"


def test_patch(client):
    client.post("/servers", json=data())
    assert client.patch("/servers/1", json={"cpu": 55}).json()["cpu"] == 55


def test_delete(client):
    client.post("/servers", json=data())
    assert client.delete("/servers/1").status_code == 204


def test_repeat_delete(client):
    client.post("/servers", json=data())
    client.delete("/servers/1")
    assert client.delete("/servers/1").status_code == 404


def test_filter(client):
    client.post("/servers", json=data("a", "10.0.0.1", 20, "online"))
    client.post("/servers", json=data("b", "10.0.0.2", 30, "offline"))
    assert len(client.get("/servers", params={"status": "offline"}).json()) == 1


def test_sort(client):
    client.post("/servers", json=data("a", "10.0.0.1", 20))
    client.post("/servers", json=data("b", "10.0.0.2", 80))
    assert client.get("/servers", params={"sort": "cpu", "order": "desc"}).json()[0]["hostname"] == "b"


def test_pagination(client):
    client.post("/servers", json=data("a", "10.0.0.1", 20))
    client.post("/servers", json=data("b", "10.0.0.2", 30))
    assert len(client.get("/servers", params={"skip": 1, "limit": 1}).json()) == 1


def test_search(client):
    client.post("/servers", json=data("web-1", "10.0.0.1", 20))
    assert len(client.get("/servers", params={"search": "web"}).json()) == 1


def test_statistics(client):
    client.post("/servers", json=data("a", "10.0.0.1", 20, "online"))
    client.post("/servers", json=data("b", "10.0.0.2", 40, "offline"))
    result = client.get("/servers/statistics").json()
    assert result["total"] == 2 and result["offline"] == 1


def test_openapi(client):
    assert client.get("/openapi.json").status_code == 200
