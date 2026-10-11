from threading import Lock

from models import Server


class ServerRepository:
    def __init__(self) -> None:
        self.items: dict[int, Server] = {}
        self.lock = Lock()

    def add(self, server: Server) -> Server:
        with self.lock:
            self.items[server.id] = server
        return server

    def get(self, server_id: int) -> Server | None:
        with self.lock:
            return self.items.get(server_id)

    def get_all(self) -> list[Server]:
        with self.lock:
            return list(self.items.values())

    def update(self, server: Server) -> Server:
        with self.lock:
            self.items[server.id] = server
        return server

    def delete(self, server_id: int) -> bool:
        with self.lock:
            return self.items.pop(server_id, None) is not None
