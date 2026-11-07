from redis_cache import RedisMetricsCache


def main() -> None:
    cache = RedisMetricsCache()
    data = {"cpu_load": 45, "memory_load": 62, "status": "online"}
    cache.set_metrics(1, data)
    cache.set_ttl(1, 60)
    print("SET:", data)
    print("GET:", cache.get_metrics(1))
    print("INCR:", cache.increment_requests())
    cache.delete_metrics(1)
    print("DELETE:", cache.get_metrics(1))


if __name__ == "__main__":
    main()
