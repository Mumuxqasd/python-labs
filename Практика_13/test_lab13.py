import time

from exceptions import ServerNotFoundError, ValidationError
from memory_storage import MemoryMongoRepository, MemoryRedisCache
from service import ServerMonitoringService


def make_service():
    return ServerMonitoringService(MemoryMongoRepository(), MemoryRedisCache())


def sample(name="srv", status="online"):
    return {
        "hostname": name,
        "ip": "10.0.0.1",
        "os_name": "Linux",
        "characteristics": {"cpu": "4 cores"},
        "services": [{"name": "http"}],
        "history": [{"status": status}],
    }


def test_add():
    service = make_service()
    assert service.add_server(sample())


def test_get():
    service = make_service()
    server_id = service.add_server(sample())
    assert service.get_server(server_id)["hostname"] == "srv"


def test_update():
    service = make_service()
    server_id = service.add_server(sample())
    assert service.update_server(server_id, {"ip": "10.0.0.2"})["ip"] == "10.0.0.2"


def test_delete():
    service = make_service()
    server_id = service.add_server(sample())
    service.delete_server(server_id)
    try:
        service.get_server(server_id)
        assert False
    except ServerNotFoundError:
        assert True


def test_search():
    service = make_service()
    service.add_server(sample("web-1"))
    assert len(service.search("web")) == 1


def test_statistics():
    service = make_service()
    service.add_server(sample("a"))
    service.add_server(sample("b"))
    assert service.statistics()[0]["servers_count"] == 2


def test_cache_aside():
    service = make_service()
    server_id = service.add_server(sample())
    assert service.get_server(server_id)["cache"] == "miss"
    assert service.get_server(server_id)["cache"] == "hit"


def test_cache_invalidation():
    service = make_service()
    server_id = service.add_server(sample())
    service.get_server(server_id)
    service.update_server(server_id, {"ip": "10.0.0.9"})
    assert service.get_server(server_id)["cache"] == "miss"


def test_problem_servers():
    service = make_service()
    service.add_server(sample("bad", "offline"))
    assert service.refresh_problem_cache() == ["bad"]


def test_clear_cache():
    service = make_service()
    server_id = service.add_server(sample())
    service.get_server(server_id)
    service.clear_cache()
    assert service.get_server(server_id)["cache"] == "miss"


def test_validation():
    service = make_service()
    try:
        service.add_server(sample(name=""))
        assert False
    except ValidationError:
        assert True


def test_ttl():
    cache = MemoryRedisCache()
    cache.set_server("1", {"a": 1}, ttl=1)
    assert cache.get_server("1") == {"a": 1}
    time.sleep(1.05)
    assert cache.get_server("1") is None
