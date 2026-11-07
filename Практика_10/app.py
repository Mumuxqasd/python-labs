from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from exceptions import ServerNotFoundError, ValidationError
from repository import ServerRepository
from service import ServerService


app = FastAPI(title="Server Monitoring API")
repository = ServerRepository()
service = ServerService(repository)


@app.exception_handler(ServerNotFoundError)
async def not_found_handler(request: Request, exc: ServerNotFoundError):
    return JSONResponse(status_code=404, content={"error": str(exc), "code": "SERVER_NOT_FOUND"})


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"error": str(exc), "code": "VALIDATION_ERROR"})


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Некорректный запрос", "code": "BAD_REQUEST"})


@app.get("/servers")
def get_servers(
    status: str | None = None,
    min_cpu: float | None = None,
    max_cpu: float | None = None,
    sort: str | None = None,
    order: str = "asc",
):
    return [server.to_dict() for server in service.get_servers(status, min_cpu, max_cpu, sort, order)]


@app.get("/servers/down")
def get_down_servers():
    return [server.to_dict() for server in service.get_down_servers()]


@app.get("/servers/{server_id}")
def get_server(server_id: int):
    if server_id <= 0:
        raise ValidationError("ID должен быть положительным")
    return service.get_server(server_id).to_dict()


@app.post("/servers", status_code=201)
def create_server(data: dict):
    return service.create_server(data).to_dict()


@app.put("/servers/{server_id}")
def put_server(server_id: int, data: dict):
    return service.put_server(server_id, data).to_dict()


@app.patch("/servers/{server_id}")
def patch_server(server_id: int, data: dict):
    return service.patch_server(server_id, data).to_dict()


@app.delete("/servers/{server_id}", status_code=204)
def delete_server(server_id: int):
    service.delete_server(server_id)
    return Response(status_code=204)
