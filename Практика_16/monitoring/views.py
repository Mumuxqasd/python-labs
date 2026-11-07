from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Prefetch, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IncidentForm, ServerForm
from .models import Incident, Metric, Server, Service


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "monitoring/index.html")


@login_required
def server_list(request: HttpRequest) -> HttpResponse:
    queryset = Server.objects.select_related("owner").all()
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    sort = request.GET.get("sort", "hostname")
    if search:
        queryset = queryset.filter(Q(hostname__icontains=search) | Q(ip__icontains=search))
    if status:
        queryset = queryset.filter(status=status)
    if sort not in {"hostname", "status", "os_name"}:
        sort = "hostname"
    if request.GET.get("order") == "desc":
        sort = "-" + sort
    paginator = Paginator(queryset.order_by(sort), 5)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "monitoring/server_list.html", {"page": page})


@login_required
def server_detail(request: HttpRequest, pk: int) -> HttpResponse:
    server = get_object_or_404(
        Server.objects.select_related("owner").prefetch_related("services", "metrics", "incidents"),
        pk=pk,
    )
    return render(request, "monitoring/server_detail.html", {"server": server})


@login_required
def server_create(request: HttpRequest) -> HttpResponse:
    form = ServerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        server = form.save(commit=False)
        server.owner = request.user
        server.save()
        return redirect("server_detail", pk=server.pk)
    return render(request, "monitoring/form.html", {"form": form, "title": "Создание сервера"})


@login_required
def server_edit(request: HttpRequest, pk: int) -> HttpResponse:
    server = get_object_or_404(Server, pk=pk)
    form = ServerForm(request.POST or None, instance=server)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("server_detail", pk=pk)
    return render(request, "monitoring/form.html", {"form": form, "title": "Редактирование сервера"})


@login_required
def server_delete(request: HttpRequest, pk: int) -> HttpResponse:
    server = get_object_or_404(Server, pk=pk)
    if request.method == "POST":
        server.delete()
        return redirect("server_list")
    return render(request, "monitoring/confirm_delete.html", {"server": server})


@login_required
def incident_create(request: HttpRequest, server_id: int) -> HttpResponse:
    server = get_object_or_404(Server, pk=server_id)
    form = IncidentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        incident = form.save(commit=False)
        incident.server = server
        incident.save()
        return redirect("server_detail", pk=server_id)
    return render(request, "monitoring/form.html", {"form": form, "title": "Регистрация инцидента"})


@login_required
def statistics(request: HttpRequest) -> HttpResponse:
    data = {
        "servers": Server.objects.count(),
        "offline": Server.objects.filter(status="offline").count(),
        "incidents": Incident.objects.filter(status="open").count(),
        "average_cpu": Metric.objects.aggregate(value=Avg("cpu"))["value"] or 0,
    }
    return render(request, "monitoring/statistics.html", data)
