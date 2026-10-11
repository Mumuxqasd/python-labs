from exceptions import ServerNotFoundError, ValidationError
from models import Server
from repository import ServerRepository


class ServerService:
    allowed_statuses = {"online", "offline", "maintenance"}

    def __init__(self, repository: ServerRepository) -> None:
        self.repository = repository
        self.next_id = 1

    def list_servers(self) -> list[Server]:
        return self.repository.get_all()

    def get_server(self, server_id: int) -> Server:
        server = self.repository.get(server_id)
        if server is None:
            raise ServerNotFoundError("Сервер не найден")
        return server

    def create_server(self, data: dict) -> Server:
        self._validate(data, full=True)
        server = Server(
            self.next_id,
            str(data["name"]).strip(),
            str(data["host"]).strip(),
            str(data["status"]).strip(),
            float(data["cpu_load"]),
        )
        self.next_id += 1
        return self.repository.add(server)

    def update_server(self, server_id: int, data: dict) -> Server:
        server = self.get_server(server_id)
        merged = server.to_dict()
        merged.update(data)
        merged.pop("id", None)
        self._validate(merged, full=True)
        server.name = str(merged["name"]).strip()
        server.host = str(merged["host"]).strip()
        server.status = str(merged["status"]).strip()
        server.cpu_load = float(merged["cpu_load"])
        return self.repository.update(server)

    def delete_server(self, server_id: int) -> None:
        self.get_server(server_id)
        self.repository.delete(server_id)

    def get_states(self) -> list[dict]:
        return [
            {
                "id": server.id,
                "name": server.name,
                "status": server.status,
                "cpu_load": server.cpu_load,
            }
            for server in self.list_servers()
        ]

    def _validate(self, data: dict, full: bool) -> None:
        required = {"name", "host", "status", "cpu_load"}
        if full and not required.issubset(data):
            raise ValidationError("Не хватает обязательных полей")
        if not str(data.get("name", "")).strip():
            raise ValidationError("Имя сервера не может быть пустым")
        if not str(data.get("host", "")).strip():
            raise ValidationError("Host не может быть пустым")
        status = str(data.get("status", ""))
        if status not in self.allowed_statuses:
            raise ValidationError("Статус: online, offline или maintenance")
        try:
            cpu = float(data.get("cpu_load"))
        except (TypeError, ValueError):
            raise ValidationError("cpu_load должен быть числом")
        if not 0 <= cpu <= 100:
            raise ValidationError("cpu_load должен быть от 0 до 100")
