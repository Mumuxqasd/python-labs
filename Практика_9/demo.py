import socket
import subprocess
import sys
import time

from client import send_request


def show(title: str, response: dict) -> None:
    print(f"{title}: {response}")


def main() -> None:
    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №9 ===")
    process = subprocess.Popen(
        [sys.executable, "-u", "server.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        started = False
        for _ in range(20):
            try:
                with socket.create_connection(("127.0.0.1", 9090), timeout=0.2):
                    started = True
                    break
            except OSError:
                time.sleep(0.2)
        if not started:
            raise RuntimeError("Не удалось запустить TCP-сервер")
        print("TCP-сервер автоматически запущен на 127.0.0.1:9090")

        first = send_request({
            "command": "create",
            "data": {
                "name": "web-1",
                "host": "10.0.0.10",
                "status": "online",
                "cpu_load": 35,
            },
        })
        second = send_request({
            "command": "create",
            "data": {
                "name": "db-1",
                "host": "10.0.0.20",
                "status": "maintenance",
                "cpu_load": 62,
            },
        })
        show("CREATE web-1", first)
        show("CREATE db-1", second)

        show("LIST", send_request({"command": "list", "data": {}}))
        show("STATUS", send_request({"command": "status", "data": {}}))

        show(
            "UPDATE web-1",
            send_request({
                "command": "update",
                "data": {
                    "id": 1,
                    "name": "web-1",
                    "host": "10.0.0.10",
                    "status": "online",
                    "cpu_load": 48,
                },
            }),
        )
        show("GET web-1", send_request({"command": "get", "data": {"id": 1}}))

        show(
            "ОШИБОЧНЫЙ ЗАПРОС",
            send_request({
                "command": "create",
                "data": {
                    "name": "bad-server",
                    "host": "10.0.0.99",
                    "status": "online",
                    "cpu_load": 150,
                },
            }),
        )

        show("DELETE db-1", send_request({"command": "delete", "data": {"id": 2}}))
        show("ИТОГОВЫЙ LIST", send_request({"command": "list", "data": {}}))
        print("Демонстрация завершена успешно.")
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    main()
