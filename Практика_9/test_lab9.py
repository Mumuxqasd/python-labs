from exceptions import ProtocolError, ServerNotFoundError
from protocol import encode_message, parse_message
from repository import ServerRepository
from service import ServerService


def sample_data():
    return {"name": "srv-1", "host": "10.0.0.1", "status": "online", "cpu_load": 25}


def test_repository_add_and_get():
    repository = ServerRepository()
    service = ServerService(repository)
    server = service.create_server(sample_data())
    assert repository.get(server.id) == server


def test_repository_delete():
    repository = ServerRepository()
    service = ServerService(repository)
    server = service.create_server(sample_data())
    assert repository.delete(server.id) is True
    assert repository.get(server.id) is None


def test_service_update():
    service = ServerService(ServerRepository())
    server = service.create_server(sample_data())
    updated = service.update_server(server.id, {"cpu_load": 55})
    assert updated.cpu_load == 55


def test_service_not_found():
    service = ServerService(ServerRepository())
    try:
        service.get_server(999)
        assert False
    except ServerNotFoundError:
        assert True


def test_protocol_json_line():
    message = {"command": "list", "data": {}}
    encoded = encode_message(message)
    assert encoded.endswith(b"\n")
    assert parse_message(encoded) == message
