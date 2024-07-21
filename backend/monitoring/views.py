
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dynamic_fields.mixins import DynamicFieldsViewMixin

from .models import Node
from .checks import CheckStatus
from . import models
from . import serializers


@api_view()
def overview(request):
    return Response({
        "n_nodes": Node.objects.count(),
        "n_positioned_nodes": Node.objects.filter(lat__isnull=False, lon__isnull=False).count(),
        "n_unknown_nodes": models.UnknownNode.objects.count(),
        "n_ok_nodes": len([n for n in Node.objects.all() if n.check_results.status() == CheckStatus.OK]),  # TODO very inefficient
    })


class NodeViewSet(DynamicFieldsViewMixin, ModelViewSet):
    """View/Edit/Add/Delete Node items."""

    queryset = models.Node.objects.all()
    serializer_class = serializers.NodeSerializer


class ServiceViewSet(ModelViewSet):
    """View/Edit/Add/Delete Service items."""

    queryset = models.Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class AlertsViewSet(ModelViewSet):
    """View/Edit/Add/Delete Alert items."""

    queryset = models.Alert.objects.all()
    serializer_class = serializers.AlertSerializer

class MeshViewSet(ModelViewSet):
    """View/Edit/Add/Delete Mesh items."""

    queryset = models.Mesh.objects.all()
    serializer_class = serializers.MeshSerializer


class UnknownNodeViewSet(ModelViewSet):
    """View/Edit/Add/Delete UnknownNode items."""

    queryset = models.UnknownNode.objects.all()
    serializer_class = serializers.UnknownNodeSerializer