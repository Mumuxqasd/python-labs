import ipaddress
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MaxLengthValidator,
)
from .validators import validate_host, validate_path


class Node(models.Model):
    name = models.CharField(max_length=100, unique=True)
    host = models.CharField(max_length=253, validators=[validate_host])
    description = models.TextField(
        blank=True, default="", validators=[MaxLengthValidator(500)]
    )
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name

    @property
    def status(self):
        if not self.enabled:
            return "PAUSED"
        checks = [c for c in self.checks.all() if c.enabled]
        if not checks:
            return "UNKNOWN"
        if any(c.last_status == "DOWN" for c in checks):
            return "DOWN"
        return "UP" if all(c.last_status == "UP" for c in checks) else "UNKNOWN"


class MonitorCheck(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="checks")
    name = models.CharField(max_length=100)
    check_type = models.CharField(
        max_length=4, choices=[(x, x) for x in ["ICMP", "TCP", "DNS", "HTTP"]]
    )
    port = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
    )
    scheme = models.CharField(
        max_length=5,
        choices=[("http", "http"), ("https", "https")],
        blank=True,
        default="",
    )
    path = models.CharField(
        max_length=255, blank=True, default="", validators=[validate_path]
    )
    expected_http_status = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(100), MaxValueValidator(599)],
    )
    interval_seconds = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(5), MaxValueValidator(300)]
    )
    timeout_seconds = models.PositiveIntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    enabled = models.BooleanField(default=True)
    last_started_at = models.DateTimeField(null=True, blank=True)
    manual_requested_at = models.DateTimeField(null=True, blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(
        max_length=7,
        default="UNKNOWN",
        choices=[(x, x) for x in ["UNKNOWN", "UP", "DOWN"]],
    )
    last_latency_ms = models.FloatField(null=True, blank=True)
    last_error = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["node_id", "id"]
        constraints = [
            models.UniqueConstraint(fields=["node", "name"], name="unique_node_check")
        ]

    def __str__(self):
        return f"{self.node}: {self.name}"

    def clean(self):
        errors = {}
        if self.timeout_seconds >= self.interval_seconds:
            errors["timeout_seconds"] = "Тайм-аут должен быть меньше интервала."
        if self.check_type == "TCP" and not self.port:
            errors["port"] = "Для TCP нужен порт."
        if self.check_type == "DNS":
            try:
                ipaddress.ip_address(self.node.host)
            except ValueError:
                pass
            else:
                errors["node"] = "DNS требует доменное имя, а не IP."
        if self.check_type == "HTTP":
            self.scheme = self.scheme or "http"
            self.path = self.path or "/"
            self.expected_http_status = self.expected_http_status or 200
            try:
                validate_path(self.path)
            except ValidationError as e:
                errors["path"] = e.messages
        else:
            self.scheme, self.path, self.expected_http_status = "", "", None
        if self.check_type not in ["TCP", "HTTP"]:
            self.port = None
        if errors:
            raise ValidationError(errors)


class CheckResult(models.Model):
    monitor = models.ForeignKey(
        MonitorCheck,
        db_column="check_id",
        on_delete=models.CASCADE,
        related_name="results",
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    status = models.CharField(max_length=4, choices=[("UP", "UP"), ("DOWN", "DOWN")])
    latency_ms = models.FloatField(null=True, validators=[MinValueValidator(0)])
    http_status = models.PositiveIntegerField(null=True)
    details = models.JSONField(default=dict)
    error_message = models.CharField(max_length=500, null=True)

    class Meta:
        ordering = ["-finished_at", "-id"]
        indexes = [
            models.Index(
                fields=["monitor", "-finished_at"], name="result_check_finished_idx"
            )
        ]


class Incident(models.Model):
    monitor = models.ForeignKey(
        MonitorCheck,
        db_column="check_id",
        on_delete=models.CASCADE,
        related_name="incidents",
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    close_reason = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        choices=[("RECOVERED", "RECOVERED"), ("STOPPED", "STOPPED")],
    )
    last_error = models.CharField(max_length=500)

    class Meta:
        ordering = ["-started_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["monitor"],
                condition=Q(ended_at__isnull=True),
                name="one_open_incident",
            )
        ]


class WorkerHeartbeat(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    last_seen_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(id=1), name="singleton_heartbeat")
        ]
