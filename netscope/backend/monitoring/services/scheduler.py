from django.db import transaction, close_old_connections
from django.utils import timezone
from ..models import Node, MonitorCheck
from .monitoring import signature, save_result
from .probes import bounded_probe


def due(check, now):
    return bool(
        check.manual_requested_at
        or not check.last_started_at
        or (now - check.last_started_at).total_seconds() >= check.interval_seconds
    )


def claim(check_id):
    with transaction.atomic():
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
            .filter(pk=check_id, enabled=True, node__enabled=True)
            .first()
        )
        now = timezone.now()
        if check is None or not due(check, now):
            return None
        check.last_started_at = now
        check.save(update_fields=["last_started_at"])
        return check, now, signature(check)


def execute_claim(job):
    close_old_connections()
    try:
        check, started, config_signature = job
        outcome = bounded_probe(check)
        save_result(check.pk, started, outcome, config_signature)
    finally:
        close_old_connections()
