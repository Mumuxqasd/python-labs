from fastapi.testclient import TestClient

from app import app, service


def show(title: str, response) -> None:
    print(title, "HTTP", response.status_code, response.json() if response.content else "")


def main() -> None:
    service.reset()
    client = TestClient(app)
    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №10 ===")
    show("POST web-1", client.post("/servers", json={"name": "web-1", "host": "10.0.0.10", "status": "online", "cpu_load": 35}))
    show("POST db-1", client.post("/servers", json={"name": "db-1", "host": "10.0.0.20", "status": "offline", "cpu_load": 80}))
    show("GET list", client.get("/servers"))
    show("GET id=1", client.get("/servers/1"))
    show("PATCH id=1", client.patch("/servers/1", json={"cpu_load": 48}))
    show("FILTER offline", client.get("/servers", params={"status": "offline"}))
    show("SORT cpu desc", client.get("/servers", params={"sort": "cpu_load", "order": "desc"}))
    show("GET down", client.get("/servers/down"))
    show("GET missing", client.get("/servers/999"))
    response = client.delete("/servers/2")
    print("DELETE id=2 HTTP", response.status_code)
    show("FINAL list", client.get("/servers"))
    print("Демонстрация завершена успешно.")


if __name__ == "__main__":
    main()
