import ipaddress
import re
from django.core.exceptions import ValidationError


def validate_host(value):
    try:
        ipaddress.ip_address(value)
        return
    except ValueError:
        pass
    if (
        len(value) > 253
        or not value
        or not all(
            re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label)
            for label in value.rstrip(".").split(".")
        )
    ):
        raise ValidationError("Введите доменное имя, IPv4 или IPv6 без схемы и порта.")


def validate_path(value):
    if (
        not value.startswith("/")
        or value.startswith("//")
        or any(ord(c) < 32 or c.isspace() for c in value)
        or "#" in value
        or "\\" in value
    ):
        raise ValidationError(
            "Путь должен начинаться с одного / и не содержать пробелы, # или управляющие символы."
        )
