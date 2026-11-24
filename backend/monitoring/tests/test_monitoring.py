import json
import socket
import subprocess
import threading
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from monitoring.models import Node, MonitorCheck, CheckResult, Incident, WorkerHeartbeat
from monitoring.serializers import NodeSerializer, CheckSerializer
from monitoring.services.probes import probe, ProbeResult
from monitoring.services.monitoring import (
    save_result,
    stop_incidents,
    cleanup_results,
    signature,
)
from monitoring.services.scheduler import claim, due


class MonitoringTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            "admin", "admin@example.test", "test-password-893"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.node = Node.objects.create(name="Test", host="127.0.0.1")
        self.check = MonitorCheck.objects.create(
            node=self.node, name="TCP", check_type="TCP", port=80
        )

    def result(self, status="DOWN"):
        return save_result(
            self.check.pk,
            timezone.now(),
            ProbeResult(
                status,
                1.2 if status == "UP" else None,
                error_message="Connection refused" if status == "DOWN" else None,
            ),
        )

    def test_create_node(self):
        response = self.client.post(
            "/api/nodes/", {"name": "Server", "host": "backend"}
        )
        self.assertEqual(response.status_code, 201)

    def test_invalid_hosts(self):
        for host in [
            "https://abc",
            "abc:80",
            "abc;id",
            "-bad",
            "a..b",
            "abc/a",
            "abc$(id)",
        ]:
            s = NodeSerializer(data={"name": "Other", "host": host})
            self.assertFalse(s.is_valid(), host)

    def test_empty_name(self):
        self.assertFalse(
            NodeSerializer(data={"name": "", "host": "backend"}).is_valid()
        )

    def test_unique_node(self):
        self.assertEqual(
            self.client.post("/api/nodes/", {"name": "Test", "host": "db"}).status_code,
            400,
        )

    def test_check_types(self):
        domain = Node.objects.create(name="Domain", host="backend")
        for kind in ["ICMP", "TCP", "DNS", "HTTP"]:
            data = {"node": domain.pk, "name": kind, "check_type": kind}
            if kind == "TCP":
                data["port"] = 5432
            response = self.client.post("/api/checks/", data, format="json")
            self.assertEqual(response.status_code, 201, response.data)
            if kind == "HTTP":
                self.assertEqual(response.data["path"], "/")

    def test_invalid_numbers(self):
        for extra in [
            {"port": 0},
            {"port": 65536},
            {"interval_seconds": 4},
            {"interval_seconds": 301},
            {"timeout_seconds": 0},
            {"timeout_seconds": 11},
            {"timeout_seconds": 5, "interval_seconds": 5},
        ]:
            data = {
                "node": self.node.pk,
                "name": "Other",
                "check_type": "TCP",
                "port": 80,
                **extra,
            }
            self.assertEqual(
                self.client.post("/api/checks/", data, format="json").status_code,
                400,
                extra,
            )

    def test_dns_disallows_ip(self):
        self.assertEqual(
            self.client.post(
                "/api/checks/",
                {"node": self.node.pk, "name": "DNS", "check_type": "DNS"},
                format="json",
            ).status_code,
            400,
        )

    def test_http_path_validation(self):
        for path in ["https://other", "//evil", "/x y", "/x#frag", "/a\\b"]:
            s = CheckSerializer(
                data={
                    "node": self.node.pk,
                    "name": "HTTP",
                    "check_type": "HTTP",
                    "path": path,
                }
            )
            self.assertFalse(s.is_valid(), path)

    def test_unused_fields_cleared(self):
        s = CheckSerializer(
            data={
                "node": self.node.pk,
                "name": "ICMP",
                "check_type": "ICMP",
                "port": 80,
                "scheme": "http",
                "path": "/",
                "expected_http_status": 200,
            }
        )
        self.assertTrue(s.is_valid(), s.errors)
        c = s.save()
        self.assertIsNone(c.port)
        self.assertEqual(c.path, "")

    def test_tcp_real_success(self):
        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            server.listen()
            self.check.port = server.getsockname()[1]
            outcome = probe(self.check)
            self.assertEqual(outcome.status, "UP")
            self.assertGreaterEqual(outcome.latency_ms, 0)

    def test_tcp_closed_port(self):
        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            port = server.getsockname()[1]
        self.check.port = port
        outcome = probe(self.check)
        self.assertEqual(outcome.status, "DOWN")
        self.assertIsNone(outcome.latency_ms)

    def test_http_real_server(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            self.check.check_type = "HTTP"
            self.check.port = server.server_port
            self.check.scheme = "http"
            self.check.path = "/"
            self.check.expected_http_status = 200
            outcome = probe(self.check)
            self.assertEqual(outcome.status, "UP")
            self.assertEqual(outcome.http_status, 200)
            self.check.expected_http_status = 204
            self.assertEqual(probe(self.check).status, "DOWN")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    @patch("monitoring.services.probes.httpx.Client")
    def test_http_redirect_not_followed(self, client):
        response = (
            client.return_value.__enter__.return_value.stream.return_value.__enter__.return_value
        )
        response.status_code = 302
        self.check.check_type = "HTTP"
        self.check.scheme = "http"
        self.check.path = "/"
        self.check.expected_http_status = 200
        self.assertEqual(probe(self.check).status, "DOWN")
        self.assertFalse(client.call_args.kwargs["follow_redirects"])

    @patch(
        "monitoring.services.probes.httpx.Client", side_effect=TimeoutError("Timed out")
    )
    def test_http_timeout(self, _):
        self.check.check_type = "HTTP"
        self.check.scheme = "http"
        self.check.path = "/"
        self.assertEqual(probe(self.check).status, "DOWN")

    @patch(
        "monitoring.services.probes.resolve_addresses",
        side_effect=OSError("DNS unavailable"),
    )
    def test_dns_error(self, _):
        self.check.check_type = "DNS"
        self.assertEqual(probe(self.check).status, "DOWN")

    @patch(
        "monitoring.services.probes.resolve_addresses", return_value=["10.0.0.2", "::1"]
    )
    def test_dns_success(self, _):
        self.check.check_type = "DNS"
        self.assertEqual(probe(self.check).details["addresses"], ["10.0.0.2", "::1"])

    @patch("monitoring.services.probes.subprocess.run")
    def test_icmp_safe_command(self, run):
        run.return_value = MagicMock(returncode=0)
        self.check.check_type = "ICMP"
        self.assertEqual(probe(self.check).status, "UP")
        self.assertNotIn("shell", run.call_args.kwargs)
        self.assertEqual(run.call_args.args[0][-1], "127.0.0.1")
        self.assertEqual(run.call_args.kwargs["timeout"], 3)

    @patch(
        "monitoring.services.probes.subprocess.run",
        side_effect=subprocess.TimeoutExpired("ping", 3),
    )
    def test_icmp_timeout(self, _):
        self.check.check_type = "ICMP"
        self.assertEqual(probe(self.check).status, "DOWN")

    def test_incident_not_duplicated(self):
        self.result()
        self.result()
        self.assertEqual(Incident.objects.count(), 1)
        self.assertEqual(CheckResult.objects.count(), 2)

    def test_recovery(self):
        self.result()
        self.result("UP")
        i = Incident.objects.get()
        self.assertIsNotNone(i.ended_at)
        self.assertEqual(i.close_reason, "RECOVERED")

    def test_disable_check_stops_incident(self):
        self.result()
        self.assertEqual(
            self.client.patch(
                f"/api/checks/{self.check.pk}/", {"enabled": False}
            ).status_code,
            200,
        )
        self.assertEqual(Incident.objects.get().close_reason, "STOPPED")

    def test_disable_node_stops_incident(self):
        self.result()
        self.client.patch(f"/api/nodes/{self.node.pk}/", {"enabled": False})
        self.assertEqual(Incident.objects.get().close_reason, "STOPPED")

    def test_old_result_cannot_reopen_incident_after_pause(self):
        config = signature(self.check)
        self.client.patch(f"/api/checks/{self.check.pk}/", {"enabled": False})
        save_result(
            self.check.pk,
            timezone.now(),
            ProbeResult("DOWN", error_message="refused"),
            config,
        )
        self.assertEqual(CheckResult.objects.count(), 1)
        self.assertEqual(Incident.objects.count(), 0)

    def test_result_and_series_ordering(self):
        r1 = self.result()
        r2 = self.result("UP")
        rows = self.client.get("/api/results/").data["results"]
        self.assertEqual([r["id"] for r in rows], [r2.pk, r1.pk])
        series = self.client.get(f"/api/checks/{self.check.pk}/series/").data
        self.assertEqual([r["status"] for r in series], ["DOWN", "UP"])

    def test_anonymous_denied(self):
        client = APIClient()
        for path in [
            "nodes/",
            "checks/",
            "results/",
            "incidents/",
            "dashboard/",
            "auth/me/",
        ]:
            self.assertIn(client.get("/api/" + path).status_code, [401, 403])
        self.assertIn(
            client.post("/api/nodes/", {"name": "No", "host": "db"}).status_code,
            [401, 403],
        )

    def test_authenticated_crud(self):
        r = self.client.post("/api/nodes/", {"name": "CRUD", "host": "db"})
        pk = r.data["id"]
        self.assertEqual(
            self.client.patch(f"/api/nodes/{pk}/", {"description": "changed"}).data[
                "description"
            ],
            "changed",
        )
        self.assertEqual(self.client.delete(f"/api/nodes/{pk}/").status_code, 204)

    def test_manual_queue_conflict_and_save(self):
        self.assertEqual(
            self.client.post(f"/api/checks/{self.check.pk}/run/").status_code, 202
        )
        self.assertEqual(
            self.client.post(f"/api/checks/{self.check.pk}/run/").status_code, 409
        )
        job = claim(self.check.pk)
        save_result(self.check.pk, job[1], ProbeResult("UP", 1.1), job[2])
        self.check.refresh_from_db()
        self.assertIsNone(self.check.manual_requested_at)
        self.assertEqual(self.check.results.count(), 1)

    def test_running_conflict(self):
        self.assertIsNotNone(claim(self.check.pk))
        self.assertEqual(
            self.client.post(f"/api/checks/{self.check.pk}/run/").status_code, 409
        )

    def test_paused_cannot_run(self):
        self.check.enabled = False
        self.check.save()
        self.assertEqual(
            self.client.post(f"/api/checks/{self.check.pk}/run/").status_code, 400
        )

    def test_cascade(self):
        self.result()
        self.client.delete(f"/api/nodes/{self.node.pk}/")
        self.assertEqual(MonitorCheck.objects.count(), 0)
        self.assertEqual(CheckResult.objects.count(), 0)
        self.assertEqual(Incident.objects.count(), 0)

    def test_cleanup_preserves_incidents(self):
        old = self.result()
        self.result("UP")
        CheckResult.objects.filter(pk=old.pk).update(
            finished_at=timezone.now() - timedelta(days=8)
        )
        self.assertEqual(cleanup_results(), 1)
        self.assertEqual(CheckResult.objects.count(), 1)
        self.assertEqual(Incident.objects.count(), 1)

    def test_node_states(self):
        self.assertEqual(self.node.status, "UNKNOWN")
        self.result("UP")
        self.assertEqual(self.node.status, "UP")
        self.result()
        self.assertEqual(self.node.status, "DOWN")
        self.node.enabled = False
        self.assertEqual(self.node.status, "PAUSED")

    def test_dashboard_heartbeat(self):
        self.assertFalse(self.client.get("/api/dashboard/").data["worker"]["running"])
        WorkerHeartbeat.objects.create(last_seen_at=timezone.now())
        self.assertTrue(self.client.get("/api/dashboard/").data["worker"]["running"])
        WorkerHeartbeat.objects.update(
            last_seen_at=timezone.now() - timedelta(seconds=16)
        )
        self.assertFalse(self.client.get("/api/dashboard/").data["worker"]["running"])

    def test_pagination_filter_and_invalid_dates(self):
        self.result()
        self.result("UP")
        r = self.client.get("/api/results/?status=DOWN&page_size=1")
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(len(r.data["results"]), 1)
        for suffix in ["from=nonsense", "from=2026-01-01", "node_id=abc"]:
            self.assertEqual(
                self.client.get("/api/results/?" + suffix).status_code, 400
            )

    def test_csrf_login_logout(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertEqual(
            client.post(
                "/api/auth/login/",
                {"username": "admin", "password": "test-password-893"},
                format="json",
            ).status_code,
            403,
        )
        client.get("/api/auth/csrf/")
        csrf = client.cookies["csrftoken"].value
        response = client.post(
            "/api/auth/login/",
            {"username": "admin", "password": "test-password-893"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.get("/api/auth/me/").status_code, 200)
        self.assertEqual(
            client.post(
                "/api/auth/logout/", HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value
            ).status_code,
            200,
        )
        self.assertEqual(client.get("/api/auth/me/").status_code, 403)

    def test_login_generic_error(self):
        client = APIClient()
        a = client.post(
            "/api/auth/login/", {"username": "admin", "password": "bad"}, format="json"
        )
        b = client.post(
            "/api/auth/login/", {"username": "nobody", "password": "bad"}, format="json"
        )
        self.assertEqual(a.json(), b.json())

    def test_scheduler_no_catchup_burst(self):
        self.check.last_started_at = timezone.now() - timedelta(days=1)
        self.check.save()
        self.assertTrue(due(self.check, timezone.now()))
        self.assertIsNotNone(claim(self.check.pk))
        self.assertIsNone(claim(self.check.pk))

    def test_bounded_probe_real_tcp(self):
        from monitoring.services.probes import bounded_probe

        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            server.listen()
            self.check.port = server.getsockname()[1]
            result = bounded_probe(self.check)
        self.assertEqual(result.status, "UP", result.error_message)

    def test_slow_http_has_global_deadline(self):
        import time
        from monitoring.services.probes import bounded_probe

        class SlowHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                time.sleep(2)
                self.send_response(200)
                self.end_headers()

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), SlowHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.check.check_type = "HTTP"
        self.check.scheme = "http"
        self.check.path = "/"
        self.check.expected_http_status = 200
        self.check.timeout_seconds = 1
        self.check.port = server.server_port
        started = time.monotonic()
        try:
            result = bounded_probe(self.check)
            self.assertEqual(result.status, "DOWN")
            self.assertIsNone(result.latency_ms)
            self.assertLess(time.monotonic() - started, 1.8)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    @patch("monitoring.services.probes.dns.resolver.Resolver")
    def test_dns_first_success_does_not_wait_for_second_family(self, resolver):
        from monitoring.services.probes import resolve_addresses

        resolver.return_value.resolve.return_value = ["10.0.0.2"]
        self.assertEqual(resolve_addresses("example.test", 1), ["10.0.0.2"])
        resolver.return_value.resolve.assert_called_once()
