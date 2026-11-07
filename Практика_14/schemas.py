from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServerCreate(BaseModel):
    hostname: str = Field(min_length=1, max_length=120)
    ip: str = Field(min_length=3, max_length=64)
    os_name: str = Field(min_length=1, max_length=120)
    cpu: float = Field(ge=0, le=100)
    ram: int = Field(gt=0)
    status: str


class ServerUpdate(BaseModel):
    hostname: str = Field(min_length=1, max_length=120)
    ip: str = Field(min_length=3, max_length=64)
    os_name: str = Field(min_length=1, max_length=120)
    cpu: float = Field(ge=0, le=100)
    ram: int = Field(gt=0)
    status: str


class ServerPatch(BaseModel):
    hostname: str | None = Field(default=None, min_length=1, max_length=120)
    ip: str | None = Field(default=None, min_length=3, max_length=64)
    os_name: str | None = Field(default=None, min_length=1, max_length=120)
    cpu: float | None = Field(default=None, ge=0, le=100)
    ram: int | None = Field(default=None, gt=0)
    status: str | None = None


class ServerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hostname: str
    ip: str
    os_name: str
    cpu: float
    ram: int
    status: str
    last_check: datetime
