from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.db import connection, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_GET, require_POST
import json
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Node, MonitorCheck, CheckResult, Incident, WorkerHeartbeat
from .serializers import (
    NodeSerializer,
    CheckSerializer,
    ResultSerializer,
    IncidentSerializer,
)
from .services.monitoring import stop_incidents, is_running


@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok", "database": "ok"})
    except Exception:
        logging.getLogger(__name__).exception("Healthcheck DB failure")
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)


@require_GET
@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"detail": "CSRF cookie set"})


@require_POST
@csrf_protect
def sign_in(request):
    try:
        data = json.loads(request.body)
        if (
            not isinstance(data, dict)
            or not isinstance(data.get("username"), str)
            or not isinstance(data.get("password"), str)
        ):
            raise ValueError()
    except (ValueError, TypeError):
        return JsonResponse({"detail": "Нужны username и password."}, status=400)
    user = authenticate(request, username=data["username"], password=data["password"])
    if not user or not user.is_staff or not user.is_active:
        return JsonResponse({"detail": "Неверный логин или пароль."}, status=400)
    login(request, user)
    return JsonResponse({"username": user.username})


@api_view(["POST"])
def sign_out(request):
    logout(request)
    return Response({"detail": "Сессия завершена"})


@api_view(["GET"])
def me(request):
    return Response({"username": request.user.username})


class NodeViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.prefetch_related("checks").all()
    serializer_class = NodeSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(host__icontains=search))
        state = self.request.query_params.get("status")
        if state:
            if state not in ["UP", "DOWN", "UNKNOWN", "PAUSED"]:
                raise ValidationError({"status": "Неизвестный статус"})
            ids = [n.pk for n in qs if n.status == state]
            qs = qs.filter(pk__in=ids)
        return qs

    @transaction.atomic
    def perform_update(self, serializer):
        Node.objects.select_for_update().get(pk=serializer.instance.pk)
        serializer.instance.refresh_from_db()
        node = serializer.save()
        if not node.enabled:
            stop_incidents(node.checks.all())
        if "host" in serializer.validated_data:
            node.checks.update(
                last_status="UNKNOWN", last_latency_ms=None, last_error=None
            )

    @transaction.atomic
    def perform_destroy(self, instance):
        Node.objects.select_for_update().get(pk=instance.pk)
        instance.delete()


class CheckViewSet(viewsets.ModelViewSet):
    queryset = MonitorCheck.objects.select_related("node").all()
    serializer_class = CheckSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get("node_id"):
            qs = qs.filter(
                node_id=integer(self.request.query_params["node_id"], "node_id")
            )
        return qs

    @transaction.atomic
    def perform_update(self, serializer):
        Node.objects.select_for_update().get(pk=serializer.instance.node_id)
        MonitorCheck.objects.select_for_update().get(pk=serializer.instance.pk)
        if (
            "node" in serializer.validated_data
            and serializer.validated_data["node"].pk != serializer.instance.node_id
        ):
            raise ValidationError(
                {"node": "Перенос проверки между узлами не поддерживается."}
            )
        serializer.instance.refresh_from_db()
        check = serializer.save()
        if not check.enabled:
            stop_incidents(MonitorCheck.objects.filter(pk=check.pk))
        if any(
            k in serializer.validated_data
            for k in [
                "check_type",
                "port",
                "scheme",
                "path",
                "expected_http_status",
                "enabled",
            ]
        ):
            MonitorCheck.objects.filter(pk=check.pk).update(
                last_status="UNKNOWN", last_latency_ms=None, last_error=None
            )

    @transaction.atomic
    def perform_destroy(self, instance):
        Node.objects.select_for_update().get(pk=instance.node_id)
        MonitorCheck.objects.select_for_update().get(pk=instance.pk)
        instance.delete()

    @action(detail=True, methods=["post"], url_path="run")
    def run_check(self, request, pk=None):
        original = self.get_object()
        with transaction.atomic():
            node = Node.objects.select_for_update().get(pk=original.node_id)
            check = MonitorCheck.objects.select_for_update().get(pk=original.pk)
            if not check.enabled or not node.enabled:
                return Response(
                    {"detail": "Сначала включите узел и проверку."}, status=400
                )
            if check.manual_requested_at or is_running(check):
                return Response(
                    {"detail": "Проверка уже запрошена или выполняется."}, status=409
                )
            check.manual_requested_at = timezone.now()
            check.save(update_fields=["manual_requested_at"])
        return Response({"detail": "Проверка запрошена"}, status=202)

    @action(detail=True, methods=["get"])
    def series(self, request, pk=None):
        check = self.get_object()
        limit = integer(request.query_params.get("limit", "60"), "limit")
        if not 1 <= limit <= 200:
            raise ValidationError({"limit": "Допустимо от 1 до 200"})
        rows = list(check.results.order_by("-finished_at", "-id")[:limit])
        return Response(
            [
                {
                    "finished_at": r.finished_at,
                    "status": r.status,
                    "latency_ms": r.latency_ms,
                }
                for r in reversed(rows)
            ]
        )


def integer(value, field):
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValidationError({field: "Ожидается целое число"})


def filter_ids(qs, params):
    for field, target in [("node_id", "monitor__node_id"), ("check_id", "monitor_id")]:
        if params.get(field):
            qs = qs.filter(**{target: integer(params[field], field)})
    return qs


class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CheckResult.objects.select_related("monitor__node").all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        params = self.request.query_params
        qs = filter_ids(super().get_queryset(), params)
        if params.get("status"):
            if params["status"] not in ["UP", "DOWN"]:
                raise ValidationError({"status": "UP или DOWN"})
            qs = qs.filter(status=params["status"])
        times = {}
        for param, lookup in [("from", "finished_at__gte"), ("to", "finished_at__lte")]:
            if params.get(param):
                try:
                    value = parse_datetime(params[param])
                except ValueError:
                    value = None
                if not value or timezone.is_naive(value):
                    raise ValidationError({param: "ISO 8601 с часовым поясом"})
                times[param] = value
                qs = qs.filter(**{lookup: value})
        if len(times) == 2 and times["from"] > times["to"]:
            raise ValidationError({"from": "Начало позже конца периода"})
        return qs


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects.select_related("monitor__node").all()
    serializer_class = IncidentSerializer

    def get_queryset(self):
        qs = filter_ids(super().get_queryset(), self.request.query_params)
        state = self.request.query_params.get("state")
        if state:
            if state not in ["open", "closed"]:
                raise ValidationError({"state": "open или closed"})
            qs = qs.filter(ended_at__isnull=state == "open")
        return qs


@api_view(["GET"])
def dashboard(request):
    nodes = list(Node.objects.prefetch_related("checks").all())
    counts = {
        s: sum(n.status == s for n in nodes)
        for s in ["UP", "DOWN", "UNKNOWN", "PAUSED"]
    }
    heartbeat = WorkerHeartbeat.objects.filter(pk=1).first()
    running = bool(
        heartbeat and timezone.now() - heartbeat.last_seen_at <= timedelta(seconds=15)
    )
    return Response(
        {
            "total_nodes": len(nodes),
            "up": counts["UP"],
            "down": counts["DOWN"],
            "unknown": counts["UNKNOWN"],
            "paused": counts["PAUSED"],
            "open_incidents": Incident.objects.filter(ended_at=None).count(),
            "worker": {
                "running": running,
                "last_seen_at": heartbeat.last_seen_at if heartbeat else None,
            },
            "latest_results": ResultSerializer(
                CheckResult.objects.select_related("monitor__node")[:10], many=True
            ).data,
        }
    )
