from rest_framework.viewsets import ModelViewSet

from . import serializers
from . import models


class RadacctViewSet(ModelViewSet):
    """View Radacct items."""

    queryset = models.Radacct.objects.all()
    serializer_class = serializers.RadacctSerializer
