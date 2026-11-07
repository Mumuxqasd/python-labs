import tempfile
from pathlib import Path

from database import init_database
from repository import SQLiteServerRepository
from service import ServerService


def main() -> None:
    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №11 ===")
    with tempfile.TemporaryDirectory() as directory:
        db_path = str(Path(directory) / "demo.db")
        init_database(db_path, with_seed=False)
        repository = SQLiteServerRepository(db_path)
        service = ServerService(repository)
        server = service.create_server({"name": "web-1", "host": "10.0.0.10", "status": "online", "cpu_load": 30})
        print("CREATE:", server.to_dict())
        repository.add_tag(server.id, "production")
        repository.add_tag(server.id, "web")
        print("TAGS:", repository.get_tags(server.id))
        service.record_metrics(server.id, 55, 60, "online")
        print("LATEST METRICS:", repository.get_latest_metrics(server.id))
        print("SERVER AFTER TRANSACTION:", service.get_server(server.id).to_dict())
        offline = service.create_server({"name": "db-1", "host": "10.0.0.20", "status": "offline", "cpu_load": 0})
        print("OFFLINE:", [item.to_dict() for item in repository.get_down_servers()])
        service.delete_server(offline.id)
        print("FINAL:", [item.to_dict() for item in service.list_servers()])
    print("Redis-часть запускается отдельно через nosql_demo.py при работающем Redis.")
    print("CDN-часть запускается через origin_server.py, cdn_server.py и cdn_demo.py.")
    print("Демонстрация завершена успешно.")


if __name__ == "__main__":
    main()
