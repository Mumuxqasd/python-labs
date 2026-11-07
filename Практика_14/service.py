from datetime import datetime

from exceptions import ServerNotFoundError, ValidationError
from models import Server
from repository import ServerRepository
from schemas import ServerCreate, ServerPatch, ServerUpdate


class ServerService:
    statuses = {"online", "offline", "maintenance"}

    def __init__(self, repository: ServerRepository) -> None:
        self.repository = repository

    def get(self, server_id: int) -> Server:
        server = self.repository.get(server_id)
        if server is None:
            raise ServerNotFoundError("Сервер не найден")
        return server

    def list(self, **params) -> list[Server]:
        return self.repository.list(**params)

    def create(self, data: ServerCreate) -> Server:
        self._check_status(data.status)
        server = Server(**data.model_dump(), last_check=datetime.utcnow())
        return self.repository.create(server)

    def put(self, server_id: int, data: ServerUpdate) -> Server:
        self._check_status(data.status)
        server = self.get(server_id)
        for key, value in data.model_dump().items():
            setattr(server, key, value)
        server.last_check = datetime.utcnow()
        return self.repository.update(server)

    def patch(self, server_id: int, data: ServerPatch) -> Server:
        server = self.get(server_id)
        changes = data.model_dump(exclude_none=True)
        if "status" in changes:
            self._check_status(changes["status"])
        for key, value in changes.items():
            setattr(server, key, value)
        server.last_check = datetime.utcnow()
        return self.repository.update(server)

    def delete(self, server_id: int) -> None:
        self.repository.delete(self.get(server_id))

    def statistics(self) -> dict:
        return self.repository.statistics()

    def _check_status(self, status: str) -> None:
        if status not in self.statuses:
            raise ValidationError("Статус: online, offline или maintenance")
