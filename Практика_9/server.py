import logging
import socket
from concurrent.futures import ThreadPoolExecutor

from exceptions import ProtocolError, ServerNotFoundError, ValidationError
from protocol import encode_message, error, ok, parse_message
from repository import ServerRepository
from service import ServerService

HOST = "127.0.0.1"
PORT = 9090

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

repository = ServerRepository()
service = ServerService(repository)


def process_request(request: dict) -> dict:
    command = request.get("command")
    data = request.get("data") or {}

    if command == "list":
        return ok([server.to_dict() for server in service.list_servers()])
    if command == "get":
        return ok(service.get_server(int(data["id"])).to_dict())
    if command == "create":
        return ok(service.create_server(data).to_dict())
    if command == "update":
        server_id = int(data.pop("id"))
        return ok(service.update_server(server_id, data).to_dict())
    if command == "delete":
        service.delete_server(int(data["id"]))
        return ok({"message": "Сервер удалён"})
    if command == "status":
        return ok(service.get_states())
    return error("Неизвестная команда")


def handle_client(connection: socket.socket, address: tuple[str, int]) -> None:
    logging.info("Подключён клиент %s", address)
    connection.settimeout(30)
    try:
        with connection, connection.makefile("rwb") as stream:
            while True:
                line = stream.readline()
                if not line:
                    break
                try:
                    request = parse_message(line)
                    logging.info("Команда: %s", request.get("command"))
                    response = process_request(request)
                except (ProtocolError, ServerNotFoundError, ValidationError, ValueError, KeyError) as exc:
                    logging.exception("Ошибка запроса")
                    response = error(str(exc))
                stream.write(encode_message(response))
                stream.flush()
    except socket.timeout:
        logging.warning("Тайм-аут клиента %s", address)
    except OSError:
        logging.exception("Ошибка соединения")
    finally:
        logging.info("Клиент отключён %s", address)


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        server_socket.settimeout(1)
        logging.info("Сервер запущен %s:%s", HOST, PORT)
        print(f"Сервер запущен на {HOST}:{PORT}")
        with ThreadPoolExecutor(max_workers=10) as pool:
            try:
                while True:
                    try:
                        connection, address = server_socket.accept()
                        pool.submit(handle_client, connection, address)
                    except socket.timeout:
                        continue
            except KeyboardInterrupt:
                print("Сервер остановлен")
                logging.info("Сервер остановлен")


if __name__ == "__main__":
    main()
