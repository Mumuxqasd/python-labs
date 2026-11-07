import logging

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from database import Base, engine, get_session
from exceptions import DuplicateError, ServerNotFoundError, ValidationError
from repository import ServerRepository
from schemas import ServerCreate, ServerOut, ServerPatch, ServerUpdate
from service import ServerService


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
Base.metadata.create_all(engine)
app = FastAPI(title="Server Monitoring FastAPI")


def get_service(session: Session = Depends(get_session)) -> ServerService:
    return ServerService(ServerRepository(session))


@app.get("/servers", response_model=list[ServerOut])
async def list_servers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    os_name: str | None = None,
    search: str | None = None,
    sort: str = "hostname",
    order: str = "asc",
    service: ServerService = Depends(get_service),
):
    return service.list(skip=skip, limit=limit, status=status, os_name=os_name, search=search, sort=sort, order=order)


@app.get("/servers/statistics")
async def statistics(service: ServerService = Depends(get_service)):
    return service.statistics()


@app.get("/servers/{server_id}", response_model=ServerOut)
async def get_server(server_id: int, service: ServerService = Depends(get_service)):
    try:
        return service.get(server_id)
    except ServerNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.post("/servers", response_model=ServerOut, status_code=201)
async def create_server(data: ServerCreate, service: ServerService = Depends(get_service)):
    try:
        return service.create(data)
    except (DuplicateError, ValidationError) as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.put("/servers/{server_id}", response_model=ServerOut)
async def put_server(server_id: int, data: ServerUpdate, service: ServerService = Depends(get_service)):
    try:
        return service.put(server_id, data)
    except ServerNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except (DuplicateError, ValidationError) as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.patch("/servers/{server_id}", response_model=ServerOut)
async def patch_server(server_id: int, data: ServerPatch, service: ServerService = Depends(get_service)):
    try:
        return service.patch(server_id, data)
    except ServerNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except (DuplicateError, ValidationError) as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.delete("/servers/{server_id}", status_code=204)
async def delete_server(server_id: int, service: ServerService = Depends(get_service)):
    try:
        service.delete(server_id)
    except ServerNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
