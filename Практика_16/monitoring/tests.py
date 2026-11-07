from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Incident, Metric, Server, Service


class MonitoringTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass12345")
        self.admin = User.objects.create_superuser(username="admin", email="admin@test.ru", password="pass12345")
        self.server = Server.objects.create(hostname="web-1", ip="10.0.0.1", os_name="Linux", status="online", owner=self.user)
        Service.objects.create(server=self.server, name="nginx", port=80, status="online")
        Metric.objects.create(server=self.server, cpu=30, ram=40)
        Incident.objects.create(server=self.server, title="Test", status="open")
        self.client = Client()

    def login(self):
        self.client.login(username="user", password="pass12345")

    def test_index(self):
        self.assertEqual(self.client.get(reverse("index")).status_code, 200)

    def test_list_requires_login(self):
        self.assertEqual(self.client.get(reverse("server_list")).status_code, 302)

    def test_list(self):
        self.login()
        self.assertEqual(self.client.get(reverse("server_list")).status_code, 200)

    def test_detail(self):
        self.login()
        self.assertEqual(self.client.get(reverse("server_detail", args=[self.server.id])).status_code, 200)

    def test_create(self):
        self.login()
        response = self.client.post(reverse("server_create"), {"hostname": "db-1", "ip": "10.0.0.2", "os_name": "Linux", "status": "offline"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Server.objects.filter(hostname="db-1").exists())

    def test_update(self):
        self.login()
        self.client.post(reverse("server_edit", args=[self.server.id]), {"hostname": "web-new", "ip": "10.0.0.1", "os_name": "Linux", "status": "maintenance"})
        self.server.refresh_from_db()
        self.assertEqual(self.server.status, "maintenance")

    def test_delete(self):
        self.login()
        self.client.post(reverse("server_delete", args=[self.server.id]))
        self.assertFalse(Server.objects.filter(id=self.server.id).exists())

    def test_search(self):
        self.login()
        response = self.client.get(reverse("server_list"), {"search": "web"})
        self.assertContains(response, "web-1")

    def test_filter(self):
        self.login()
        response = self.client.get(reverse("server_list"), {"status": "online"})
        self.assertContains(response, "web-1")

    def test_sort(self):
        self.login()
        response = self.client.get(reverse("server_list"), {"sort": "hostname", "order": "desc"})
        self.assertEqual(response.status_code, 200)

    def test_pagination(self):
        self.login()
        for i in range(6):
            Server.objects.create(hostname=f"srv-{i}", ip=f"10.0.1.{i+1}", os_name="Linux", status="online", owner=self.user)
        response = self.client.get(reverse("server_list"), {"page": 2})
        self.assertEqual(response.status_code, 200)

    def test_validation(self):
        self.login()
        response = self.client.post(reverse("server_create"), {"hostname": "", "ip": "bad", "os_name": "", "status": "online"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Server.objects.count(), 1)

    def test_authentication(self):
        self.assertFalse(self.client.get(reverse("server_list")).wsgi_request.user.is_authenticated)
        self.login()
        self.assertTrue(self.client.get(reverse("server_list")).wsgi_request.user.is_authenticated)

    def test_admin_access(self):
        self.client.login(username="admin", password="pass12345")
        self.assertEqual(self.client.get("/admin/").status_code, 200)

    def test_relations(self):
        self.assertEqual(self.server.services.count(), 1)
        self.assertEqual(self.server.metrics.count(), 1)
        self.assertEqual(self.server.incidents.count(), 1)
