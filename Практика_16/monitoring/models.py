from django.contrib.auth.models import User
from django.db import models


class Server(models.Model):
    STATUS_CHOICES = [("online", "online"), ("offline", "offline"), ("maintenance", "maintenance")]
    hostname = models.CharField(max_length=120, unique=True)
    ip = models.GenericIPAddressField(unique=True)
    os_name = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="offline")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="servers")

    def __str__(self) -> str:
        return self.hostname


class Service(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=120)
    port = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="unknown")

    def __str__(self) -> str:
        return f"{self.server.hostname}:{self.port}"


class Metric(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="metrics")
    cpu = models.FloatField()
    ram = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class Incident(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="incidents")
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=30, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
