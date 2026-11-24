import logging
import signal
import time
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from django.db import close_old_connections, DatabaseError
from django.utils import timezone
from monitoring.models import MonitorCheck, WorkerHeartbeat
from monitoring.services.scheduler import due, claim, execute_claim
from monitoring.services.monitoring import cleanup_results

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run the single NetScope worker with at most five concurrent probes."

    def handle(self, *args, **options):
        stopping = False

        def stop(*_):
            nonlocal stopping
            stopping = True

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        active = {}
        cleanup_at = 0
        with ThreadPoolExecutor(max_workers=5, thread_name_prefix="probe") as pool:
            while not stopping:
                try:
                    close_old_connections()
                    for pk, future in list(active.items()):
                        if future.done():
                            try:
                                future.result()
                            except Exception:
                                logger.exception("Probe task failed: %s", pk)
                            del active[pk]
                    WorkerHeartbeat.objects.update_or_create(
                        pk=1, defaults={"last_seen_at": timezone.now()}
                    )
                    if time.monotonic() >= cleanup_at:
                        cleanup_results()
                        cleanup_at = time.monotonic() + 86400
                    for check in MonitorCheck.objects.filter(
                        enabled=True, node__enabled=True
                    ).order_by("last_started_at", "id"):
                        if len(active) >= 5:
                            break
                        if check.pk in active or not due(check, timezone.now()):
                            continue
                        job = claim(check.pk)
                        if job:
                            active[check.pk] = pool.submit(execute_claim, job)
                except DatabaseError:
                    logger.exception("Database unavailable; retrying")
                    close_old_connections()
                except Exception:
                    logger.exception("Worker iteration failed; continuing")
                time.sleep(1)
        logger.info("Worker stopped")
