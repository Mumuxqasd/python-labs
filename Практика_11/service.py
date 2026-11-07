from exceptions import ServerNotFoundError, ValidationError
from models import Server
from repository import SQLiteServerRepository


class ServerService:
    allowed_statuses = {"online", "offline", "maintenance"}

    def __init__(self, repository: SQLiteServerRepository) -> None:
        self.repository = repository

    def list_servers(self, **filters) -> list[Server]:
        return self.repository.get_all(**filters)

    def get_server(self, server_id: int) -> Server:
        server = self.repository.get_by_id(server_id)
        if server is None:
            raise ServerNotFoundError("Сервер не найден")
        return server

    def create_server(self, data: dict) -> Server:
        self._validate(data)
        return self.repository.create(
            str(data["name"]).strip(),
            str(data["host"]).strip(),
            str(data["status"]).strip(),
            float(data["cpu_load"]),
        )

    def update_server(self, server_id: int, data: dict) -> Server:
        server = self.get_server(server_id)
        merged = server.to_dict()
        merged.update(data)
        merged.pop("id", None)
        self._validate(merged)
        server.name = str(merged["name"]).strip()
        server.host = str(merged["host"]).strip()
        server.status = str(merged["status"]).strip()
        server.cpu_load = float(merged["cpu_load"])
        return self.repository.update(server)

    def delete_server(self, server_id: int) -> None:
        self.get_server(server_id)
        self.repository.delete(server_id)

    def record_metrics(self, server_id: int, cpu_load: float, memory_load: float, status: str) -> None:
        self.get_server(server_id)
        if not 0 <= cpu_load <= 100 or not 0 <= memory_load <= 100:
            raise ValidationError("Нагрузка должна быть от 0 до 100")
        if status not in self.allowed_statuses:
            raise ValidationError("Некорректный статус")
        self.repository.record_metrics_transaction(server_id, cpu_load, memory_load, status)

    def _validate(self, data: dict) -> None:
        if not str(data.get("name", "")).strip():
            raise ValidationError("Имя сервера не может быть пустым")
        if not str(data.get("host", "")).strip():
            raise ValidationError("Host не может быть пустым")
        if str(data.get("status", "")) not in self.allowed_statuses:
            raise ValidationError("Некорректный статус")
        try:
            cpu = float(data.get("cpu_load"))
        except (TypeError, ValueError):
            raise ValidationError("cpu_load должен быть числом")
        if not 0 <= cpu <= 100:
            raise ValidationError("cpu_load должен быть от 0 до 100")
