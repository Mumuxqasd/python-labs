from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from exceptions import DuplicateError
from models import Server


class ServerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, server_id: int) -> Server | None:
        return self.session.get(Server, server_id)

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        os_name: str | None = None,
        search: str | None = None,
        sort: str = "hostname",
        order: str = "asc",
    ) -> list[Server]:
        statement = select(Server)
        if status:
            statement = statement.where(Server.status == status)
        if os_name:
            statement = statement.where(Server.os_name == os_name)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(or_(Server.hostname.ilike(pattern), Server.ip.ilike(pattern)))
        columns = {"hostname": Server.hostname, "cpu": Server.cpu, "ram": Server.ram, "last_check": Server.last_check}
        column = columns.get(sort, Server.hostname)
        statement = statement.order_by(column.desc() if order == "desc" else column.asc()).offset(skip).limit(limit)
        return list(self.session.scalars(statement).all())

    def create(self, server: Server) -> Server:
        self.session.add(server)
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise DuplicateError("hostname или IP уже используется") from error
        self.session.refresh(server)
        return server

    def update(self, server: Server) -> Server:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise DuplicateError("hostname или IP уже используется") from error
        self.session.refresh(server)
        return server

    def delete(self, server: Server) -> None:
        self.session.delete(server)
        self.session.commit()

    def statistics(self) -> dict:
        total = self.session.scalar(select(func.count(Server.id))) or 0
        offline = self.session.scalar(select(func.count(Server.id)).where(Server.status == "offline")) or 0
        average_cpu = self.session.scalar(select(func.avg(Server.cpu))) or 0
        return {"total": int(total), "offline": int(offline), "average_cpu": round(float(average_cpu), 2)}
