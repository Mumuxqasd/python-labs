from dataclasses import asdict, dataclass, field


@dataclass
class ServerDocument:
    hostname: str
    ip: str
    os_name: str
    characteristics: dict
    services: list[dict] = field(default_factory=list)
    history: list[dict] = field(default_factory=list)
    id: str | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data.pop("id", None)
        return data
