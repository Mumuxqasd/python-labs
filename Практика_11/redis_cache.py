import json

from exceptions import RedisUnavailableError


class RedisMetricsCache:
    def __init__(self, host: str = "127.0.0.1", port: int = 6379) -> None:
        self.host = host
        self.port = port

    def _client(self):
        try:
            import redis
        except ModuleNotFoundError as error:
            raise RedisUnavailableError("Установите пакет redis") from error
        client = redis.Redis(host=self.host, port=self.port, decode_responses=True)
        try:
            client.ping()
        except Exception as error:
            raise RedisUnavailableError("Redis недоступен") from error
        return client

    def set_metrics(self, server_id: int, metrics: dict) -> None:
        self._client().set(f"server:{server_id}:metrics", json.dumps(metrics, ensure_ascii=False))

    def get_metrics(self, server_id: int) -> dict | None:
        value = self._client().get(f"server:{server_id}:metrics")
        return json.loads(value) if value else None

    def delete_metrics(self, server_id: int) -> None:
        self._client().delete(f"server:{server_id}:metrics")

    def set_ttl(self, server_id: int, seconds: int) -> None:
        self._client().expire(f"server:{server_id}:metrics", seconds)

    def increment_requests(self) -> int:
        return int(self._client().incr("metrics:requests"))
