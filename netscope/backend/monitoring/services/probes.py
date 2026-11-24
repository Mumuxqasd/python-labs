"""Network operations only. No database access and no shell interpolation."""

from dataclasses import dataclass, field
import ipaddress
import socket
import subprocess
import time
import dns.resolver
import httpx


@dataclass
class ProbeResult:
    status: str
    latency_ms: float | None = None
    http_status: int | None = None
    details: dict = field(default_factory=dict)
    error_message: str | None = None


def resolve_addresses(host, timeout):
    try:
        return [str(ipaddress.ip_address(host))]
    except ValueError:
        pass
    resolver = dns.resolver.Resolver()
    deadline = time.monotonic() + timeout
    addresses = []
    for kind in ["A", "AAAA"]:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            answer = resolver.resolve(host, kind, lifetime=remaining, search=False)
            addresses.extend(str(a) for a in answer)
            if addresses:
                break  # One successful A/AAAA answer is enough; do not wait for the other family.
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            raise
        except dns.exception.Timeout:
            if not addresses:
                raise
    if not addresses:
        raise OSError("DNS не вернул A/AAAA адреса")
    return addresses


def probe(check):
    start = time.monotonic()
    timeout = check.timeout_seconds
    code = None
    details = {}
    try:
        host = check.node.host
        if check.check_type == "ICMP":
            completed = subprocess.run(
                ["ping", "-n", "-c", "1", "-W", str(timeout), "--", host],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if completed.returncode:
                raise OSError(
                    (completed.stderr or completed.stdout or "Нет ICMP-ответа").strip()[
                        :500
                    ]
                )
        elif check.check_type == "DNS":
            details["addresses"] = resolve_addresses(host, timeout)
        elif check.check_type == "TCP":
            addresses = resolve_addresses(host, timeout)
            error = None
            for address in addresses:
                remaining = timeout - (time.monotonic() - start)
                if remaining <= 0:
                    raise TimeoutError("TCP: истёк тайм-аут")
                try:
                    with socket.create_connection(
                        (address, check.port), timeout=remaining
                    ):
                        pass
                    details = {"port": check.port, "address": address}
                    break
                except OSError as e:
                    error = e
            else:
                raise error or OSError("Не удалось подключиться")
        elif check.check_type == "HTTP":
            address = f"[{host}]" if ":" in host else host
            port = f":{check.port}" if check.port else ""
            url = f"{check.scheme}://{address}{port}{check.path}"
            # Stream only headers; do not read or retain response bodies/cookies.
            with httpx.Client(
                timeout=timeout, follow_redirects=False, trust_env=False
            ) as client:
                with client.stream("GET", url) as response:
                    code = response.status_code
            if code != check.expected_http_status:
                raise OSError(f"HTTP {code}; ожидался {check.expected_http_status}")
        else:
            raise ValueError("Неизвестный тип проверки")
        return ProbeResult(
            "UP", round((time.monotonic() - start) * 1000, 3), code, details
        )
    except Exception as e:
        return ProbeResult(
            "DOWN",
            http_status=code,
            details=details,
            error_message=(str(e) or type(e).__name__)[:500],
        )


def bounded_probe(check):
    """Isolate blocking OS DNS/TLS I/O and enforce a wall-clock deadline.

    A socket timeout alone does not bound getaddrinfo or slow HTTP headers.
    A short-lived child is killed as a process group on deadline; at most five
    such children exist because the worker owns a bounded thread pool.
    """
    import json
    import os
    import signal
    import sys
    from pathlib import Path

    payload = {
        key: getattr(check, key)
        for key in [
            "check_type",
            "port",
            "scheme",
            "path",
            "expected_http_status",
            "timeout_seconds",
        ]
    }
    payload["host"] = check.node.host
    process = subprocess.Popen(
        [sys.executable, "-m", "monitoring.services.probe_runner"],
        cwd=Path(__file__).resolve().parents[2],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        output, _ = process.communicate(
            json.dumps(payload), timeout=check.timeout_seconds
        )
        if process.returncode:
            return ProbeResult(
                "DOWN", error_message="Процесс проверки завершился с ошибкой"
            )
        return ProbeResult(**json.loads(output))
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()
        return ProbeResult(
            "DOWN", error_message=f"Истёк тайм-аут проверки ({check.timeout_seconds} с)"
        )
    except Exception as exc:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.communicate()
        return ProbeResult("DOWN", error_message=str(exc)[:500])
