from database import connect
from models import Server


class SQLiteServerRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def get_all(
        self,
        status: str | None = None,
        min_cpu: float | None = None,
        max_cpu: float | None = None,
        sort: str | None = None,
        order: str = "asc",
    ) -> list[Server]:
        sql = "SELECT id, name, host, status, cpu_load FROM servers WHERE 1=1"
        params: list[object] = []
        if status is not None:
            sql += " AND status = ?"
            params.append(status)
        if min_cpu is not None:
            sql += " AND cpu_load >= ?"
            params.append(min_cpu)
        if max_cpu is not None:
            sql += " AND cpu_load <= ?"
            params.append(max_cpu)
        if sort in {"name", "cpu_load"}:
            direction = "DESC" if order == "desc" else "ASC"
            sql += f" ORDER BY {sort} {direction}"
        connection = connect(self.db_path)
        try:
            rows = connection.execute(sql, params).fetchall()
            return [Server(**dict(row)) for row in rows]
        finally:
            connection.close()

    def get_by_id(self, server_id: int) -> Server | None:
        connection = connect(self.db_path)
        try:
            row = connection.execute(
                "SELECT id, name, host, status, cpu_load FROM servers WHERE id = ?",
                (server_id,),
            ).fetchone()
            return Server(**dict(row)) if row else None
        finally:
            connection.close()

    def create(self, name: str, host: str, status: str, cpu_load: float) -> Server:
        connection = connect(self.db_path)
        try:
            cursor = connection.execute(
                "INSERT INTO servers(name, host, status, cpu_load) VALUES (?, ?, ?, ?)",
                (name, host, status, cpu_load),
            )
            connection.commit()
            server_id = cursor.lastrowid
        finally:
            connection.close()
        server = self.get_by_id(server_id)
        if server is None:
            raise RuntimeError("Не удалось создать сервер")
        return server

    def update(self, server: Server) -> Server:
        connection = connect(self.db_path)
        try:
            connection.execute(
                "UPDATE servers SET name = ?, host = ?, status = ?, cpu_load = ? WHERE id = ?",
                (server.name, server.host, server.status, server.cpu_load, server.id),
            )
            connection.commit()
        finally:
            connection.close()
        result = self.get_by_id(server.id)
        if result is None:
            raise RuntimeError("Не удалось обновить сервер")
        return result

    def delete(self, server_id: int) -> bool:
        connection = connect(self.db_path)
        try:
            cursor = connection.execute("DELETE FROM servers WHERE id = ?", (server_id,))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    def get_down_servers(self) -> list[Server]:
        return self.get_all(status="offline")

    def add_tag(self, server_id: int, tag_name: str) -> None:
        connection = connect(self.db_path)
        try:
            connection.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (tag_name,))
            tag_id = connection.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()[0]
            connection.execute(
                "INSERT OR IGNORE INTO server_tags(server_id, tag_id) VALUES (?, ?)",
                (server_id, tag_id),
            )
            connection.commit()
        finally:
            connection.close()

    def get_tags(self, server_id: int) -> list[str]:
        connection = connect(self.db_path)
        try:
            rows = connection.execute(
                "SELECT t.name FROM tags t JOIN server_tags st ON st.tag_id = t.id WHERE st.server_id = ? ORDER BY t.name",
                (server_id,),
            ).fetchall()
            return [row[0] for row in rows]
        finally:
            connection.close()

    def record_metrics_transaction(self, server_id: int, cpu_load: float, memory_load: float, status: str) -> None:
        connection = connect(self.db_path)
        try:
            connection.execute("BEGIN")
            cursor = connection.execute(
                "UPDATE servers SET cpu_load = ?, status = ? WHERE id = ?",
                (cpu_load, status, server_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("Сервер не найден")
            connection.execute(
                "INSERT INTO metrics(server_id, cpu_load, memory_load) VALUES (?, ?, ?)",
                (server_id, cpu_load, memory_load),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def get_latest_metrics(self, server_id: int) -> dict | None:
        connection = connect(self.db_path)
        try:
            row = connection.execute(
                "SELECT id, server_id, cpu_load, memory_load, captured_at FROM metrics WHERE server_id = ? ORDER BY captured_at DESC, id DESC LIMIT 1",
                (server_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()

    def get_metrics(self, server_id: int) -> list[dict]:
        connection = connect(self.db_path)
        try:
            rows = connection.execute(
                "SELECT id, server_id, cpu_load, memory_load, captured_at FROM metrics WHERE server_id = ? ORDER BY id",
                (server_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()
