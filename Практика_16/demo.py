import os


def main() -> None:
    print("=== ДЕМОНСТРАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ №16 ===")
    try:
        import django
    except ModuleNotFoundError:
        print("Django не установлен в текущем окружении.")
        print("После установки выполните python manage.py migrate и python demo.py.")
        return
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from django.contrib.auth.models import User
    from django.core.management import call_command
    from django.test import Client
    from monitoring.models import Incident, Metric, Server, Service
    call_command("migrate", verbosity=0)
    Server.objects.all().delete()
    User.objects.filter(username="demo").delete()
    user = User.objects.create_user(username="demo", password="demo12345")
    server = Server.objects.create(hostname="web-1", ip="10.0.0.1", os_name="Linux", status="online", owner=user)
    Service.objects.create(server=server, name="nginx", port=80, status="online")
    Metric.objects.create(server=server, cpu=35, ram=42)
    Incident.objects.create(server=server, title="Высокая нагрузка", status="open")
    client = Client()
    client.login(username="demo", password="demo12345")
    print("LIST HTTP:", client.get("/servers/").status_code)
    print("DETAIL HTTP:", client.get(f"/servers/{server.id}/").status_code)
    print("STATISTICS HTTP:", client.get("/statistics/").status_code)
    print("SERVERS:", list(Server.objects.values_list("hostname", "status")))
    print("SERVICES:", list(Service.objects.values_list("name", "status")))
    print("METRICS:", list(Metric.objects.values_list("cpu", "ram")))
    print("INCIDENTS:", list(Incident.objects.values_list("title", "status")))
    print("Демонстрация завершена успешно.")


if __name__ == "__main__":
    main()
