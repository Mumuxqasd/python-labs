"""Real probes through the worker in Docker; no internet or API mocks."""

import time
from django.core.management.base import BaseCommand, CommandError
from monitoring.models import Node, MonitorCheck, Incident, CheckResult
from django.utils import timezone


class Command(BaseCommand):
    help = "Exercise real TCP/HTTP and UP → DOWN → UP. --verify checks persistence after restart."

    def add_arguments(self, parser):
        parser.add_argument("--verify", action="store_true")

    def wait(self, check, expected, after):
        for _ in range(90):
            check.refresh_from_db()
            if (
                check.last_checked_at
                and check.last_checked_at > after
                and check.last_status == expected
            ):
                return
            time.sleep(1)
        raise CommandError(f"No {expected} result within 90s: {check.last_error}")

    def handle(self, *args, **opts):
        if opts["verify"]:
            check = MonitorCheck.objects.get(
                node__name="Acceptance · backend", name="TCP lifecycle"
            )
            if (
                check.results.count() < 3
                or not check.incidents.filter(close_reason="RECOVERED").exists()
            ):
                raise CommandError("Missing persisted history/incidents")
            self.stdout.write(
                self.style.SUCCESS(
                    "PASS: persisted history and recovery survived restart"
                )
            )
            return
        node, _ = Node.objects.get_or_create(
            name="Acceptance · backend", defaults={"host": "backend"}
        )
        if node.host != "backend":
            raise CommandError("Acceptance node has been edited; use another database")
        node.enabled = True
        node.save()
        check, _ = MonitorCheck.objects.get_or_create(
            node=node,
            name="TCP lifecycle",
            defaults={"check_type": "TCP", "port": 8000, "interval_seconds": 5},
        )
        for port, expected in [(8000, "UP"), (59999, "DOWN"), (8000, "UP")]:
            since = timezone.now()
            MonitorCheck.objects.filter(pk=check.pk).update(
                port=port, enabled=True, manual_requested_at=since
            )
            self.wait(check, expected, since)
            self.stdout.write(f"PASS: TCP {port} → {expected}")
        if not Incident.objects.filter(
            monitor=check, close_reason="RECOVERED"
        ).exists():
            raise CommandError("Recovery incident missing")
        http, _ = MonitorCheck.objects.get_or_create(
            node=node,
            name="HTTP health",
            defaults={
                "check_type": "HTTP",
                "scheme": "http",
                "port": 8000,
                "path": "/api/health/",
                "expected_http_status": 200,
                "interval_seconds": 5,
            },
        )
        since = timezone.now()
        MonitorCheck.objects.filter(pk=http.pk).update(manual_requested_at=since)
        self.wait(http, "UP", since)
        self.stdout.write(
            self.style.SUCCESS("PASS: real Docker TCP/HTTP; failure/recovery recorded")
        )
