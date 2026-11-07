from pathlib import Path

import pytest

from database import connect, init_database
from exceptions import ServerNotFoundError, ValidationError
from repository import SQLiteServerRepository
from service import ServerService


def make_service(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    init_database(db_path, with_seed=False)
    repository = SQLiteServerRepository(db_path)
    return ServerService(repository), repository, db_path


def data(name="srv", status="online", cpu=20):
    return {"name": name, "host": "10.0.0.1", "status": status, "cpu_load": cpu}


def test_create(tmp_path):
    service, repository, _ = make_service(tmp_path)
    assert service.create_server(data()).id == 1


def test_read(tmp_path):
    service, repository, _ = make_service(tmp_path)
    server = service.create_server(data())
    assert service.get_server(server.id).name == "srv"


def test_update(tmp_path):
    service, repository, _ = make_service(tmp_path)
    server = service.create_server(data())
    assert service.update_server(server.id, {"cpu_load": 50}).cpu_load == 50


def test_delete(tmp_path):
    service, repository, _ = make_service(tmp_path)
    server = service.create_server(data())
    service.delete_server(server.id)
    with pytest.raises(ServerNotFoundError):
        service.get_server(server.id)


def test_validation(tmp_path):
    service, repository, _ = make_service(tmp_path)
    with pytest.raises(ValidationError):
        service.create_server(data(cpu=150))


def test_filter(tmp_path):
    service, repository, _ = make_service(tmp_path)
    service.create_server(data("a", "online", 20))
    service.create_server(data("b", "offline", 0))
    assert len(repository.get_down_servers()) == 1


def test_transaction(tmp_path):
    service, repository, _ = make_service(tmp_path)
    server = service.create_server(data())
    service.record_metrics(server.id, 60, 70, "maintenance")
    assert service.get_server(server.id).cpu_load == 60
    assert len(repository.get_metrics(server.id)) == 1


def test_tags_many_to_many(tmp_path):
    service, repository, _ = make_service(tmp_path)
    server = service.create_server(data())
    repository.add_tag(server.id, "production")
    repository.add_tag(server.id, "critical")
    assert repository.get_tags(server.id) == ["critical", "production"]


def test_indexes_exist(tmp_path):
    service, repository, db_path = make_service(tmp_path)
    connection = connect(db_path)
    try:
        names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'index'").fetchall()}
    finally:
        connection.close()
    assert "idx_servers_status" in names
    assert "idx_metrics_server_time" in names


def test_latest_metrics(tmp_path):
    service, repository, _ = make_service(tmp_path)
    server = service.create_server(data())
    service.record_metrics(server.id, 33, 44, "online")
    assert repository.get_latest_metrics(server.id)["memory_load"] == 44
