import csv
import json
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from exceptions import StorageError


class Repository(ABC):
    @abstractmethod
    def save(self, objects):
        pass

    @abstractmethod
    def load(self):
        pass


class JsonRepository(Repository):
    def __init__(self, path, object_type, backup_dir=None):
        self.path = Path(path)
        self.object_type = object_type
        self.backup_dir = Path(backup_dir) if backup_dir else None

    def _backup(self):
        if not self.path.exists() or not self.backup_dir:
            return
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        target = self.backup_dir / f"{self.path.stem}_{stamp}{self.path.suffix}"
        shutil.copy2(self.path, target)

    def save(self, objects):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._backup()
            with self.path.open("w", encoding="utf-8") as file:
                json.dump([obj.to_dict() for obj in objects], file, ensure_ascii=False, indent=4)
        except OSError as error:
            raise StorageError(f"Не удалось сохранить JSON: {error}") from error

    def load(self):
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as file:
                raw = json.load(file)
            if not isinstance(raw, list):
                raise StorageError("Корень JSON должен быть списком")
            return [self.object_type.from_dict(item) for item in raw]
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise StorageError(f"Некорректный JSON-файл {self.path}: {error}") from error


def export_clients_csv(clients, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["name", "tariff", "speed", "monthly_fee", "connected"],
            )
            writer.writeheader()
            for client in clients:
                writer.writerow(client.to_dict())
    except OSError as error:
        raise StorageError(f"Не удалось экспортировать CSV: {error}") from error


def import_clients_csv(path, client_type):
    path = Path(path)
    if not path.exists():
        raise StorageError(f"CSV-файл не найден: {path}")
    try:
        result = []
        with path.open("r", newline="", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                row["connected"] = str(row.get("connected", "")).lower() in {"1", "true", "да", "yes"}
                result.append(client_type.from_dict(row))
        return result
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise StorageError(f"Не удалось импортировать CSV: {error}") from error
