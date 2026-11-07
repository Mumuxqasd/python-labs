from exceptions import ServerNotFoundError, ValidationError
from models import Server
from repository import ServerRepository


class ServerService:
    allowed_statuses = {"online", "offline", "maintenance"}

    def __init__(self, repository: ServerRepository) -> None:
        self.repository = repository
        self.next_id = 1

    def reset(self) -> None:
        self.repository.clear()
        self.next_id = 1

    def get_servers(
        self,
        status: str | None = None,
        min_cpu: float | None = None,
        max_cpu: float | None = None,
        sort: str | None = None,
        order: str = "asc",
    ) -> list[Server]:
        result = self.repository.get_all()
        if status is not None:
            result = [server for server in result if server.status == status]
        if min_cpu is not None:
            result = [server for server in result if server.cpu_load >= min_cpu]
        if max_cpu is not None:
            result = [server for server in result if server.cpu_load <= max_cpu]
        if sort is not None:
            if sort not in {"name", "cpu_load"}:
                raise ValidationError("Сортировка: name или cpu_load")
            if order not in {"asc", "desc"}:
                raise ValidationError("Порядок: asc или desc")
            result = sorted(
                result,
                key=lambda server: getattr(server, sort),
                reverse=order == "desc",
            )
        return result

    def get_server(self, server_id: int) -> Server:
        server = self.repository.get_by_id(server_id)
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
        return self.repository.create(server)

    def put_server(self, server_id: int, data: dict) -> Server:
        self.get_server(server_id)
        self._validate(data, full=True)
        server = Server(
            server_id,
            str(data["name"]).strip(),
            str(data["host"]).strip(),
            str(data["status"]).strip(),
            float(data["cpu_load"]),
        )
        return self.repository.update(server)

    def patch_server(self, server_id: int, data: dict) -> Server:
        server = self.get_server(server_id)
        merged = server.to_dict()
        merged.update(data)
        merged.pop("id", None)
        return self.put_server(server_id, merged)

    def delete_server(self, server_id: int) -> None:
        self.get_server(server_id)
        self.repository.delete(server_id)

    def get_down_servers(self) -> list[Server]:
        return [server for server in self.repository.get_all() if server.status == "offline"]

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
