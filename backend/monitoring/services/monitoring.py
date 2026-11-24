from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from ..models import Node, MonitorCheck, CheckResult, Incident

CONFIG_FIELDS = [
    "node_id",
    "check_type",
    "port",
    "scheme",
    "path",
    "expected_http_status",
    "interval_seconds",
    "timeout_seconds",
    "enabled",
]


def signature(check):
    return tuple(getattr(check, k) for k in CONFIG_FIELDS) + (
        check.node.host,
        check.node.enabled,
    )


def is_running(check):
    return bool(
        check.last_started_at
        and (not check.last_checked_at or check.last_started_at > check.last_checked_at)
        and (timezone.now() - check.last_started_at).total_seconds()
        < check.timeout_seconds * 3 + 10
    )


def stop_incidents(checks):
    ids = list(checks.values_list("pk", flat=True))
    Incident.objects.filter(monitor_id__in=ids, ended_at=None).update(
        ended_at=timezone.now(), close_reason="STOPPED"
    )
    MonitorCheck.objects.filter(pk__in=ids).update(manual_requested_at=None)


@transaction.atomic
def save_result(check_id, started_at, outcome, expected_signature=None):
    # Lock in the same order as the API: node, then check.
    node_id = (
        MonitorCheck.objects.filter(pk=check_id)
        .values_list("node_id", flat=True)
        .first()
    )
    if node_id is None:
        return None
    Node.objects.select_for_update().get(pk=node_id)
    check = (
        MonitorCheck.objects.select_for_update()
        .select_related("node")
        .filter(pk=check_id)
        .first()
    )
    if not check:
        return None
    finished = timezone.now()
    result = CheckResult.objects.create(
        monitor=check,
        started_at=started_at,
        finished_at=finished,
        status=outcome.status,
        latency_ms=outcome.latency_ms if outcome.status == "UP" else None,
        http_status=outcome.http_status,
        details=outcome.details,
        error_message=outcome.error_message,
    )
    check.manual_requested_at = None
    check.last_checked_at = finished
    # An in-flight old configuration may finish after an edit/pause. Keep history,
    # but never overwrite the current state or reopen a stopped incident.
    current = expected_signature is None or signature(check) == expected_signature
    if current and check.enabled and check.node.enabled:
        check.last_status, check.last_latency_ms, check.last_error = (
            result.status,
            result.latency_ms,
            result.error_message,
        )
        incident = Incident.objects.filter(monitor=check, ended_at=None).first()
        if result.status == "DOWN":
            if incident:
                incident.last_error = result.error_message or "Ошибка проверки"
                incident.save(update_fields=["last_error"])
            else:
                Incident.objects.create(
                    monitor=check,
                    started_at=started_at,
                    last_error=result.error_message or "Ошибка проверки",
                )
        elif incident:
            incident.ended_at, incident.close_reason = finished, "RECOVERED"
            incident.save(update_fields=["ended_at", "close_reason"])
    check.save(
        update_fields=[
            "manual_requested_at",
            "last_checked_at",
            "last_status",
            "last_latency_ms",
            "last_error",
        ]
    )
    return result


def cleanup_results():
    return CheckResult.objects.filter(
        finished_at__lt=timezone.now() - timedelta(days=7)
    ).delete()[0]
