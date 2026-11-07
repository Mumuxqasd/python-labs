from flask import Blueprint, redirect, render_template, request, url_for

from ..database import SessionLocal
from ..repositories.repositories import SmartHomeRepository
from ..services.services import SmartHomeService


web = Blueprint("web", __name__)


def make_service(session):
    return SmartHomeService(SmartHomeRepository(session))


@web.get("/")
def index():
    return render_template("index.html")


@web.get("/devices")
def device_list():
    with SessionLocal() as session:
        service = make_service(session)
        devices = service.list_devices(request.args.get("search"), request.args.get("status"), request.args.get("sort", "name"))
        return render_template("list.html", devices=devices)


@web.get("/devices/<int:device_id>")
def device_detail(device_id: int):
    with SessionLocal() as session:
        service = make_service(session)
        try:
            device = service.get_device(device_id)
            measurements = service.repository.measurements(device_id)
            return render_template("detail.html", device=device, measurements=measurements)
        except ValueError:
            return render_template("404.html"), 404


@web.route("/devices/create", methods=["GET", "POST"])
def device_create():
    if request.method == "POST":
        with SessionLocal() as session:
            service = make_service(session)
            try:
                service.create_device(int(request.form["user_id"]), request.form["name"], request.form["device_type"], request.form["room"], request.form["status"])
                return redirect(url_for("web.device_list"))
            except Exception as error:
                return render_template("create.html", error=str(error)), 400
    return render_template("create.html", error=None)


@web.route("/devices/<int:device_id>/edit", methods=["GET", "POST"])
def device_edit(device_id: int):
    with SessionLocal() as session:
        service = make_service(session)
        try:
            device = service.get_device(device_id)
            if request.method == "POST":
                service.update_device(device_id, request.form["name"], request.form["room"], request.form["status"])
                return redirect(url_for("web.device_detail", device_id=device_id))
            return render_template("edit.html", device=device, error=None)
        except Exception as error:
            return render_template("404.html", error=str(error)), 404


@web.post("/devices/<int:device_id>/delete")
def device_delete(device_id: int):
    with SessionLocal() as session:
        service = make_service(session)
        service.delete_device(device_id)
    return redirect(url_for("web.device_list"))
