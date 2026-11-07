from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("servers/", views.server_list, name="server_list"),
    path("servers/create/", views.server_create, name="server_create"),
    path("servers/<int:pk>/", views.server_detail, name="server_detail"),
    path("servers/<int:pk>/edit/", views.server_edit, name="server_edit"),
    path("servers/<int:pk>/delete/", views.server_delete, name="server_delete"),
    path("servers/<int:server_id>/incidents/create/", views.incident_create, name="incident_create"),
    path("statistics/", views.statistics, name="statistics"),
]
