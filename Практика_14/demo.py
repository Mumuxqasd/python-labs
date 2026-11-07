import os
from pathlib import Path

from fastapi.testclient import TestClient


def main() -> None:
    db = Path(__file__).resolve().parent / "lab14.db"
    if db.exists():
        db.unlink()
    from app import app
    client = TestClient(app)
    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №14 ===")
    data1 = {"hostname": "web-1", "ip": "10.0.0.10", "os_name": "Linux", "cpu": 35, "ram": 8192, "status": "online"}
    data2 = {"hostname": "db-1", "ip": "10.0.0.20", "os_name": "Linux", "cpu": 75, "ram": 16384, "status": "offline"}
    print("POST 1:", client.post("/servers", json=data1).json())
    print("POST 2:", client.post("/servers", json=data2).json())
    print("LIST:", client.get("/servers").json())
    print("SEARCH web:", client.get("/servers", params={"search": "web"}).json())
    print("FILTER offline:", client.get("/servers", params={"status": "offline"}).json())
    print("SORT cpu desc:", client.get("/servers", params={"sort": "cpu", "order": "desc"}).json())
    print("PAGINATION:", client.get("/servers", params={"skip": 0, "limit": 1}).json())
    print("PATCH:", client.patch("/servers/1", json={"cpu": 48}).json())
    print("STATISTICS:", client.get("/servers/statistics").json())
    print("404:", client.get("/servers/999").status_code)
    print("DELETE:", client.delete("/servers/2").status_code)
    print("OPENAPI:", client.get("/openapi.json").status_code)
    print("Демонстрация завершена успешно.")


if __name__ == "__main__":
    main()
