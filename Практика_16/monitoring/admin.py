from django.contrib import admin

from .models import Incident, Metric, Server, Service


admin.site.register(Server)
admin.site.register(Service)
admin.site.register(Metric)
admin.site.register(Incident)
