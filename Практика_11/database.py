import sqlite3
from pathlib import Path


def connect(db_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database(db_path: str, with_seed: bool = True) -> None:
    base = Path(__file__).resolve().parent
    connection = connect(db_path)
    try:
        connection.executescript((base / "schema.sql").read_text(encoding="utf-8"))
        if with_seed:
            count = connection.execute("SELECT COUNT(*) FROM servers").fetchone()[0]
            if count == 0:
                connection.executescript((base / "seed.sql").read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()
