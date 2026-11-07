from flask import Blueprint, jsonify, request

from ..database import SessionLocal
from ..repositories.repositories import SmartHomeRepository
from ..services.services import SmartHomeService


api = Blueprint("api", __name__)


def make_service(session):
    return SmartHomeService(SmartHomeRepository(session))


@api.get("/devices")
def api_list():
    with SessionLocal() as session:
        devices = make_service(session).list_devices(request.args.get("search"), request.args.get("status"), request.args.get("sort", "name"))
        return jsonify([{"id": d.id, "name": d.name, "type": d.device_type, "room": d.room, "status": d.status} for d in devices])


@api.get("/devices/<int:device_id>")
def api_get(device_id: int):
    with SessionLocal() as session:
        try:
            d = make_service(session).get_device(device_id)
            return jsonify({"id": d.id, "name": d.name, "type": d.device_type, "room": d.room, "status": d.status})
        except ValueError as error:
            return jsonify({"error": str(error)}), 404


@api.post("/devices")
def api_create():
    data = request.get_json() or {}
    with SessionLocal() as session:
        try:
            d = make_service(session).create_device(int(data["user_id"]), data["name"], data["device_type"], data["room"], data["status"])
            return jsonify({"id": d.id, "name": d.name}), 201
        except Exception as error:
            return jsonify({"error": str(error)}), 400


@api.patch("/devices/<int:device_id>")
def api_patch(device_id: int):
    data = request.get_json() or {}
    with SessionLocal() as session:
        try:
            current = make_service(session).get_device(device_id)
            d = make_service(session).update_device(device_id, data.get("name", current.name), data.get("room", current.room), data.get("status", current.status))
            return jsonify({"id": d.id, "name": d.name, "room": d.room, "status": d.status})
        except Exception as error:
            return jsonify({"error": str(error)}), 400


@api.delete("/devices/<int:device_id>")
def api_delete(device_id: int):
    with SessionLocal() as session:
        try:
            make_service(session).delete_device(device_id)
            return "", 204
        except ValueError as error:
            return jsonify({"error": str(error)}), 404
