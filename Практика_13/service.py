from time import perf_counter

from exceptions import ValidationError
from models import ServerDocument


class ServerMonitoringService:
    def __init__(self, repository, cache) -> None:
        self.repository = repository
        self.cache = cache

    def add_server(self, data: dict) -> str:
        self._validate(data)
        server = ServerDocument(
            hostname=str(data["hostname"]).strip(),
            ip=str(data["ip"]).strip(),
            os_name=str(data["os_name"]).strip(),
            characteristics=dict(data.get("characteristics", {})),
            services=list(data.get("services", [])),
            history=list(data.get("history", [])),
        )
        return self.repository.add(server)

    def get_server(self, server_id: str) -> dict:
        cached = self.cache.get_server(server_id)
        if cached is not None:
            result = dict(cached)
            result["cache"] = "hit"
            return result
        result = self.repository.get(server_id)
        self.cache.set_server(server_id, result, 60)
        result = dict(result)
        result["cache"] = "miss"
        return result

    def list_servers(self) -> list[dict]:
        return self.repository.list_all()

    def search(self, text: str) -> list[dict]:
        return self.repository.search(text)

    def update_server(self, server_id: str, changes: dict) -> dict:
        result = self.repository.update(server_id, changes)
        self.cache.delete_server(server_id)
        return result

    def delete_server(self, server_id: str) -> None:
        self.repository.delete(server_id)
        self.cache.delete_server(server_id)

    def statistics(self) -> list[dict]:
        return self.repository.statistics()

    def refresh_problem_cache(self) -> list[str]:
        problems = []
        for server in self.repository.list_all():
            history = server.get("history", [])
            if history and history[-1].get("status") in {"offline", "error"}:
                problems.append(server["hostname"])
        self.cache.set_problem_servers(problems, 60)
        return problems

    def benchmark(self, server_id: str, count: int = 100) -> dict:
        self.cache.delete_server(server_id)
        start = perf_counter()
        for _ in range(count):
            self.repository.get(server_id)
        database_time = perf_counter() - start
        self.get_server(server_id)
        start = perf_counter()
        for _ in range(count):
            self.cache.get_server(server_id)
        cache_time = perf_counter() - start
        return {"database": database_time, "cache": cache_time}

    def clear_cache(self) -> None:
        self.cache.clear()

    def _validate(self, data: dict) -> None:
        if not str(data.get("hostname", "")).strip():
            raise ValidationError("hostname не может быть пустым")
        if not str(data.get("ip", "")).strip():
            raise ValidationError("IP не может быть пустым")
        if not str(data.get("os_name", "")).strip():
            raise ValidationError("ОС не может быть пустой")
