from django import forms

from .models import Incident, Server


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ["hostname", "ip", "os_name", "status"]


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["title", "status"]
