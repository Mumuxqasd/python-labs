import socket

from protocol import encode_message, parse_message

HOST = "127.0.0.1"
PORT = 9090


def send_request(request: dict) -> dict:
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            sock.settimeout(5)
            with sock.makefile("rwb") as stream:
                stream.write(encode_message(request))
                stream.flush()
                line = stream.readline()
                if not line:
                    raise ConnectionError("Сервер закрыл соединение")
                return parse_message(line)
    except (OSError, ConnectionError) as error:
        return {"status": "error", "error": f"Ошибка соединения: {error}"}


def read_server_data(include_id: bool = False) -> dict:
    data = {}
    if include_id:
        data["id"] = int(input("ID: "))
    data["name"] = input("Имя: ")
    data["host"] = input("Host: ")
    data["status"] = input("Статус online/offline/maintenance: ")
    data["cpu_load"] = float(input("CPU, %: "))
    return data


def main() -> None:
    while True:
        print("\n=== TCP CLIENT ===")
        print("1. Список серверов")
        print("2. Получить сервер")
        print("3. Создать сервер")
        print("4. Изменить сервер")
        print("5. Удалить сервер")
        print("6. Состояние серверов")
        print("0. Выход")
        choice = input("Выберите пункт: ").strip()
        try:
            if choice == "1":
                request = {"command": "list", "data": {}}
            elif choice == "2":
                request = {"command": "get", "data": {"id": int(input("ID: "))}}
            elif choice == "3":
                request = {"command": "create", "data": read_server_data()}
            elif choice == "4":
                request = {"command": "update", "data": read_server_data(True)}
            elif choice == "5":
                request = {"command": "delete", "data": {"id": int(input("ID: "))}}
            elif choice == "6":
                request = {"command": "status", "data": {}}
            elif choice == "0":
                break
            else:
                print("Нет такого пункта")
                continue
            print(send_request(request))
        except ValueError:
            print("Ошибка ввода")


if __name__ == "__main__":
    main()
