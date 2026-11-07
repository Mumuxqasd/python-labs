from pathlib import Path

from fastapi import FastAPI, HTTPException

from database import init_database
from redis_cache import RedisMetricsCache
from repository import SQLiteServerRepository
from service import ServerService


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "servers.db")
init_database(DB_PATH, with_seed=True)
repository = SQLiteServerRepository(DB_PATH)
service = ServerService(repository)
cache = RedisMetricsCache()
app = FastAPI(title="Server Storage API")


@app.get("/servers")
def get_servers():
    return [server.to_dict() for server in service.list_servers()]


@app.get("/servers/{server_id}")
def get_server(server_id: int):
    try:
        return service.get_server(server_id).to_dict()
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.post("/servers", status_code=201)
def create_server(data: dict):
    try:
        return service.create_server(data).to_dict()
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/servers/{server_id}/metrics")
def record_metrics(server_id: int, data: dict):
    try:
        service.record_metrics(server_id, float(data["cpu_load"]), float(data["memory_load"]), str(data["status"]))
        cache.delete_metrics(server_id)
        return {"status": "ok"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/servers/{server_id}/metrics")
def get_metrics(server_id: int):
    return repository.get_metrics(server_id)


@app.get("/servers/{server_id}/current-metrics")
def current_metrics(server_id: int):
    try:
        cache.increment_requests()
        cached = cache.get_metrics(server_id)
        if cached is not None:
            return {"source": "redis", "data": cached}
    except Exception:
        pass
    metrics = repository.get_latest_metrics(server_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail="Метрики не найдены")
    try:
        cache.set_metrics(server_id, metrics)
        cache.set_ttl(server_id, 60)
    except Exception:
        pass
    return {"source": "sqlite", "data": metrics}
