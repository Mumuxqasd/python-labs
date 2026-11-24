from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework import serializers
from .models import Node, MonitorCheck, CheckResult, Incident


class NodeSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    checks_count = serializers.SerializerMethodField()
    last_checked_at = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_checks_count(self, obj):
        return len(obj.checks.all())

    def get_last_checked_at(self, obj):
        times = [c.last_checked_at for c in obj.checks.all() if c.last_checked_at]
        return max(times) if times else None

    def validate(self, attrs):
        host = attrs.get("host", getattr(self.instance, "host", None))
        if (
            self.instance
            and host != self.instance.host
            and self.instance.checks.filter(check_type="DNS").exists()
        ):
            import ipaddress

            try:
                ipaddress.ip_address(host)
            except ValueError:
                pass
            else:
                raise serializers.ValidationError(
                    {"host": "Узел с DNS-проверкой требует доменное имя."}
                )
        return attrs


class CheckSerializer(serializers.ModelSerializer):
    node_name = serializers.CharField(source="node.name", read_only=True)
    node_host = serializers.CharField(source="node.host", read_only=True)
    status = serializers.SerializerMethodField()
    running = serializers.SerializerMethodField()

    class Meta:
        model = MonitorCheck
        fields = "__all__"
        read_only_fields = [
            "last_started_at",
            "manual_requested_at",
            "last_checked_at",
            "last_status",
            "last_latency_ms",
            "last_error",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {"path": {"allow_blank": True}}

    def get_status(self, obj):
        return "PAUSED" if not obj.enabled or not obj.node.enabled else obj.last_status

    def get_running(self, obj):
        from .services.monitoring import is_running

        return is_running(obj)

    def validate(self, attrs):
        instance = self.instance
        values = {
            f.name: getattr(instance, f.name)
            for f in MonitorCheck._meta.fields
            if instance and f.name not in ["id", "node"]
        }
        if instance:
            values["node"] = instance.node
        values.update(attrs)
        candidate = MonitorCheck(**values)
        try:
            candidate.clean()
        except ModelValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        for key in ["port", "scheme", "path", "expected_http_status"]:
            attrs[key] = getattr(candidate, key)
        return attrs


class ResultSerializer(serializers.ModelSerializer):
    check = serializers.PrimaryKeyRelatedField(source="monitor", read_only=True)
    node_name = serializers.CharField(source="monitor.node.name", read_only=True)
    check_name = serializers.CharField(source="monitor.name", read_only=True)
    check_type = serializers.CharField(source="monitor.check_type", read_only=True)

    class Meta:
        model = CheckResult
        exclude = ["monitor"]


class IncidentSerializer(serializers.ModelSerializer):
    check = serializers.PrimaryKeyRelatedField(source="monitor", read_only=True)
    node_name = serializers.CharField(source="monitor.node.name", read_only=True)
    check_name = serializers.CharField(source="monitor.name", read_only=True)
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        exclude = ["monitor"]

    def get_duration_seconds(self, obj):
        from django.utils import timezone

        return round(
            ((obj.ended_at or timezone.now()) - obj.started_at).total_seconds()
        )
