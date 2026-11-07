from fastapi.testclient import TestClient

from app import app, service
from exceptions import ValidationError
from repository import ServerRepository
from service import ServerService


client = TestClient(app)


def setup_function() -> None:
    service.reset()


def data(name="srv", status="online", cpu=25):
    return {"name": name, "host": "10.0.0.1", "status": status, "cpu_load": cpu}


def test_repository_create():
    repository = ServerRepository()
    local = ServerService(repository)
    server = local.create_server(data())
    assert repository.get_by_id(server.id) == server


def test_repository_delete():
    repository = ServerRepository()
    local = ServerService(repository)
    server = local.create_server(data())
    assert repository.delete(server.id) is True


def test_service_validation():
    local = ServerService(ServerRepository())
    try:
        local.create_server(data(cpu=150))
        assert False
    except ValidationError:
        assert True


def test_service_filter():
    local = ServerService(ServerRepository())
    local.create_server(data("a", "online", 20))
    local.create_server(data("b", "offline", 70))
    assert len(local.get_servers(status="offline")) == 1


def test_service_down():
    local = ServerService(ServerRepository())
    local.create_server(data("a", "offline", 20))
    assert len(local.get_down_servers()) == 1


def test_post_and_get():
    response = client.post("/servers", json=data())
    assert response.status_code == 201
    assert client.get("/servers/1").status_code == 200


def test_put():
    client.post("/servers", json=data())
    response = client.put("/servers/1", json=data("new", "maintenance", 50))
    assert response.json()["name"] == "new"


def test_patch():
    client.post("/servers", json=data())
    response = client.patch("/servers/1", json={"cpu_load": 55})
    assert response.json()["cpu_load"] == 55


def test_delete():
    client.post("/servers", json=data())
    assert client.delete("/servers/1").status_code == 204


def test_sort_and_special_endpoint():
    client.post("/servers", json=data("a", "online", 10))
    client.post("/servers", json=data("b", "offline", 90))
    sorted_data = client.get("/servers", params={"sort": "cpu_load", "order": "desc"}).json()
    assert sorted_data[0]["name"] == "b"
    assert len(client.get("/servers/down").json()) == 1


def test_errors():
    assert client.get("/servers/999").status_code == 404
    assert client.post("/servers", json=data(cpu=-1)).status_code == 400
