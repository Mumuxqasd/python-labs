from django.core.management.base import BaseCommand
from monitoring.models import Node, MonitorCheck


class Command(BaseCommand):
    help = "Explicitly add offline demo nodes/checks. Safe to run again."

    def handle(self, *args, **kwargs):
        backend, _ = Node.objects.get_or_create(
            name="Django · демонстрация",
            defaults={"host": "backend", "description": "Локальный API"},
        )
        db, _ = Node.objects.get_or_create(
            name="PostgreSQL · демонстрация", defaults={"host": "db"}
        )
        for node, name, kind, options in [
            (
                backend,
                "API health",
                "HTTP",
                {
                    "scheme": "http",
                    "port": 8000,
                    "path": "/api/health/",
                    "expected_http_status": 200,
                },
            ),
            (backend, "DNS Docker", "DNS", {}),
            (backend, "ICMP", "ICMP", {}),
            (db, "PostgreSQL TCP", "TCP", {"port": 5432}),
            (backend, "Закрытый порт", "TCP", {"port": 59999}),
        ]:
            check, created = MonitorCheck.objects.get_or_create(
                node=node, name=name, defaults={"check_type": kind, **options}
            )
            self.stdout.write(f'{"Added" if created else "Exists"}: {check}')
