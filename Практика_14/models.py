from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    hostname: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    ip: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    os_name: Mapped[str] = mapped_column(String(120), nullable=False)
    cpu: Mapped[float] = mapped_column(Float, nullable=False)
    ram: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    last_check: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
