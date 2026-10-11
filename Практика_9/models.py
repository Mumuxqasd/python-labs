from dataclasses import dataclass, asdict


@dataclass
class Server:
    id: int
    name: str
    host: str
    status: str
    cpu_load: float

    def to_dict(self) -> dict:
        return asdict(self)
