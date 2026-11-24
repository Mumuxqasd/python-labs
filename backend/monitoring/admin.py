from django.contrib import admin
from .models import Node, MonitorCheck, CheckResult, Incident, WorkerHeartbeat


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ["name", "host", "enabled"]

    def save_model(self, request, obj, form, change):
        from .services.monitoring import stop_incidents

        super().save_model(request, obj, form, change)
        if not obj.enabled:
            stop_incidents(obj.checks.all())


@admin.register(MonitorCheck)
class CheckAdmin(admin.ModelAdmin):
    list_display = ["name", "node", "check_type", "enabled", "last_status"]
    readonly_fields = [
        "last_started_at",
        "last_checked_at",
        "last_status",
        "last_latency_ms",
        "last_error",
        "manual_requested_at",
    ]

    def save_model(self, request, obj, form, change):
        from .services.monitoring import stop_incidents

        super().save_model(request, obj, form, change)
        if not obj.enabled:
            stop_incidents(MonitorCheck.objects.filter(pk=obj.pk))


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(CheckResult, ReadOnlyAdmin)
admin.site.register(Incident, ReadOnlyAdmin)
admin.site.register(WorkerHeartbeat, ReadOnlyAdmin)
