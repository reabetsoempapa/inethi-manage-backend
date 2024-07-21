from rest_framework.serializers import ModelSerializer

from .models import Service


class ServiceSerializer(ModelSerializer):
    """Serializes Service objects from django model to JSON."""

    class Meta:
        """ServiceSerializer metadata."""

        model = Service
        fields = "__all__"
