from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Server",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hostname", models.CharField(max_length=120, unique=True)),
                ("ip", models.GenericIPAddressField(unique=True)),
                ("os_name", models.CharField(max_length=120)),
                ("status", models.CharField(choices=[("online", "online"), ("offline", "offline"), ("maintenance", "maintenance")], default="offline", max_length=20)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="servers", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("port", models.PositiveIntegerField()),
                ("status", models.CharField(default="unknown", max_length=20)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="services", to="monitoring.server")),
            ],
        ),
        migrations.CreateModel(
            name="Metric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("cpu", models.FloatField()),
                ("ram", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="metrics", to="monitoring.server")),
            ],
        ),
        migrations.CreateModel(
            name="Incident",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("status", models.CharField(default="open", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="incidents", to="monitoring.server")),
            ],
        ),
    ]
