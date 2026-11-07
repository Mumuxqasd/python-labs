import json

from exceptions import StorageUnavailableError


class RedisServerCache:
    def __init__(self, host: str = "127.0.0.1", port: int = 6379) -> None:
        try:
            import redis
        except ModuleNotFoundError as error:
            raise StorageUnavailableError("Установите redis") from error
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        try:
            self.client.ping()
        except Exception as error:
            raise StorageUnavailableError("Redis недоступен") from error

    def get_server(self, server_id: str) -> dict | None:
        value = self.client.get(f"server:{server_id}")
        return json.loads(value) if value else None

    def set_server(self, server_id: str, data: dict, ttl: int = 60) -> None:
        self.client.set(f"server:{server_id}", json.dumps(data, ensure_ascii=False), ex=ttl)

    def delete_server(self, server_id: str) -> None:
        self.client.delete(f"server:{server_id}")

    def set_current_state(self, hostname: str, state: dict, ttl: int = 60) -> None:
        self.client.set(f"state:{hostname}", json.dumps(state, ensure_ascii=False), ex=ttl)

    def get_current_state(self, hostname: str) -> dict | None:
        value = self.client.get(f"state:{hostname}")
        return json.loads(value) if value else None

    def set_problem_servers(self, hostnames: list[str], ttl: int = 60) -> None:
        key = "servers:problems"
        self.client.delete(key)
        if hostnames:
            self.client.sadd(key, *hostnames)
        self.client.expire(key, ttl)

    def get_problem_servers(self) -> list[str]:
        return sorted(self.client.smembers("servers:problems"))

    def clear(self) -> None:
        for key in self.client.scan_iter("server:*"):
            self.client.delete(key)
        for key in self.client.scan_iter("state:*"):
            self.client.delete(key)
        self.client.delete("servers:problems")
