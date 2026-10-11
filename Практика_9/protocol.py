import json

from exceptions import ProtocolError


def encode_message(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8")


def parse_message(data: bytes) -> dict:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProtocolError("Некорректный JSON") from error
    if not isinstance(value, dict):
        raise ProtocolError("Сообщение должно быть JSON-объектом")
    return value


def ok(data=None) -> dict:
    return {"status": "ok", "data": data}


def error(message: str) -> dict:
    return {"status": "error", "error": message}
