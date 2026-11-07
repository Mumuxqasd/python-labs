import copy
import time
import uuid

from exceptions import ServerNotFoundError
from models import ServerDocument


class MemoryMongoRepository:
    def __init__(self) -> None:
        self.items: dict[str, dict] = {}

    def add(self, server: ServerDocument) -> str:
        server_id = uuid.uuid4().hex[:8]
        data = server.to_dict()
        data["_id"] = server_id
        self.items[server_id] = data
        return server_id

    def get(self, server_id: str) -> dict:
        if server_id not in self.items:
            raise ServerNotFoundError("Сервер не найден")
        return copy.deepcopy(self.items[server_id])

    def list_all(self) -> list[dict]:
        return [copy.deepcopy(item) for item in sorted(self.items.values(), key=lambda x: x["hostname"])]

    def search(self, text: str) -> list[dict]:
        text = text.lower()
        return [copy.deepcopy(item) for item in self.items.values() if text in item["hostname"].lower() or text in item["ip"].lower()]

    def by_status(self, status: str) -> list[dict]:
        return [copy.deepcopy(item) for item in self.items.values() if any(event.get("status") == status for event in item.get("history", []))]

    def update(self, server_id: str, changes: dict) -> dict:
        if server_id not in self.items:
            raise ServerNotFoundError("Сервер не найден")
        self.items[server_id].update(copy.deepcopy(changes))
        return self.get(server_id)

    def delete(self, server_id: str) -> None:
        if server_id not in self.items:
            raise ServerNotFoundError("Сервер не найден")
        del self.items[server_id]

    def statistics(self) -> list[dict]:
        stats: dict[str, dict] = {}
        for item in self.items.values():
            row = stats.setdefault(item["os_name"], {"os": item["os_name"], "servers_count": 0, "services_count": 0})
            row["servers_count"] += 1
            row["services_count"] += len(item.get("services", []))
        return sorted(stats.values(), key=lambda x: x["os"])


class MemoryRedisCache:
    def __init__(self) -> None:
        self.values: dict[str, tuple[object, float | None]] = {}

    def _set(self, key: str, value, ttl: int | None = None) -> None:
        expires = time.time() + ttl if ttl else None
        self.values[key] = (copy.deepcopy(value), expires)

    def _get(self, key: str):
        item = self.values.get(key)
        if item is None:
            return None
        value, expires = item
        if expires is not None and expires <= time.time():
            self.values.pop(key, None)
            return None
        return copy.deepcopy(value)

    def get_server(self, server_id: str) -> dict | None:
        return self._get(f"server:{server_id}")

    def set_server(self, server_id: str, data: dict, ttl: int = 60) -> None:
        self._set(f"server:{server_id}", data, ttl)

    def delete_server(self, server_id: str) -> None:
        self.values.pop(f"server:{server_id}", None)

    def set_current_state(self, hostname: str, state: dict, ttl: int = 60) -> None:
        self._set(f"state:{hostname}", state, ttl)

    def get_current_state(self, hostname: str) -> dict | None:
        return self._get(f"state:{hostname}")

    def set_problem_servers(self, hostnames: list[str], ttl: int = 60) -> None:
        self._set("servers:problems", sorted(hostnames), ttl)

    def get_problem_servers(self) -> list[str]:
        return self._get("servers:problems") or []

    def clear(self) -> None:
        self.values.clear()
