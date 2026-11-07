from memory_storage import MemoryMongoRepository, MemoryRedisCache
from service import ServerMonitoringService


def main() -> None:
    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №13 ===")
    service = ServerMonitoringService(MemoryMongoRepository(), MemoryRedisCache())
    first = service.add_server({
        "hostname": "web-1",
        "ip": "10.0.0.10",
        "os_name": "Linux",
        "characteristics": {"cpu": "4 cores", "ram": "8 GB"},
        "services": [{"name": "nginx", "port": 80}],
        "history": [{"status": "online", "cpu": 35}],
    })
    second = service.add_server({
        "hostname": "db-1",
        "ip": "10.0.0.20",
        "os_name": "Linux",
        "characteristics": {"cpu": "8 cores", "ram": "16 GB"},
        "services": [{"name": "postgres", "port": 5432}],
        "history": [{"status": "offline", "cpu": 0}],
    })
    print("LIST:", service.list_servers())
    print("SEARCH web:", service.search("web"))
    print("CACHE MISS:", service.get_server(first))
    print("CACHE HIT:", service.get_server(first))
    print("PROBLEMS:", service.refresh_problem_cache())
    print("STATISTICS:", service.statistics())
    print("UPDATE:", service.update_server(first, {"ip": "10.0.0.11"}))
    service.delete_server(second)
    print("FINAL:", service.list_servers())
    print("BENCHMARK:", service.benchmark(first, 100))
    print("Реальный запуск использует MongoServerRepository и RedisServerCache.")
    print("Демонстрация завершена успешно.")


if __name__ == "__main__":
    main()
