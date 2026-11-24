from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("nodes", views.NodeViewSet)
router.register("checks", views.CheckViewSet)
router.register("results", views.ResultViewSet)
router.register("incidents", views.IncidentViewSet)
urlpatterns = [
    path("health/", views.health),
    path("auth/csrf/", views.csrf),
    path("auth/login/", views.sign_in),
    path("auth/logout/", views.sign_out),
    path("auth/me/", views.me),
    path("dashboard/", views.dashboard),
    path("", include(router.urls)),
]
