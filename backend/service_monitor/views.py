
from rest_framework.viewsets import ModelViewSet
from .models import Service

from . import serializers


class ServiceViewSet(ModelViewSet):
    """View Service items."""

    queryset = Service.objects.all()
    serializer_class = serializers.ServiceSerializer
