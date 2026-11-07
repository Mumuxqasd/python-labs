from models import Server


class ServerRepository:
    def __init__(self) -> None:
        self.items: dict[int, Server] = {}

    def get_all(self) -> list[Server]:
        return list(self.items.values())

    def get_by_id(self, server_id: int) -> Server | None:
        return self.items.get(server_id)

    def create(self, server: Server) -> Server:
        self.items[server.id] = server
        return server

    def update(self, server: Server) -> Server:
        self.items[server.id] = server
        return server

    def delete(self, server_id: int) -> bool:
        return self.items.pop(server_id, None) is not None

    def clear(self) -> None:
        self.items.clear()
