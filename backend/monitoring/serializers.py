from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    SlugRelatedField
)
from dynamic_fields.serializers import DynamicFieldsModelSerializer

from . import models


class MeshSerializer(ModelSerializer):
    """Serializes Mesh objects from django model to JSON."""

    class Meta:
        """MeshSerializer metadata."""

        model = models.Mesh
        fields = "__all__"


class AlertSerializer(ModelSerializer):
    """Serializes Alert objects from django model to JSON."""

    node = SerializerMethodField()
    type = SerializerMethodField()

    class Meta:
        """ServiceSerializer metadata."""

        model = models.Alert
        fields = "__all__"

    def get_node(self, alert):
        # The default PrimaryKeyRelatedField doesn't work, because Node's primary
        # key is a MacAddressField, and rest_framework has trouble serializing
        # that to JSON. As a workaround, I manually stringify it here.
        return str(alert.node.mac)

    def get_type(self, alert):
        return alert.type()


class ClientSessionSerializer(ModelSerializer):
    """Serializes ClientSession objects from django model to JSON."""

    uplink = SerializerMethodField()
    user = SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        """ClientSessionSerializer metadata."""

        model = models.ClientSession
        fields = "__all__"

    def get_uplink(self, client_session):
        return str(client_session.uplink.mac)


class NodeSerializer(DynamicFieldsModelSerializer):
    """Serializes Node objects from django model to JSON."""

    class Meta:
        """Node metadata."""

        model = models.Node
        fields = "__all__"

    neighbours = PrimaryKeyRelatedField(many=True, read_only=True)
    status = SerializerMethodField()
    checks = SerializerMethodField()
    latest_alerts = SerializerMethodField()
    num_unresolved_alerts = SerializerMethodField()
    upload_speed = SerializerMethodField()
    download_speed = SerializerMethodField()
    client_sessions = ClientSessionSerializer(many=True, read_only=True)

    def get_status(self, node: models.Node) -> str:
        return node.check_results.status().value

    def get_checks(self, node: models.Node) -> list[dict]:
        """Run checks defined in settings.DEVICE_CHECKS"""
        return node.check_results.serialize()

    def get_latest_alerts(self, node: models.Node) -> list[dict]:
        """Get the latest alerts for this node."""
        # TODO: Hard-coded for now
        return AlertSerializer(node.alerts.order_by("created")[:10], many=True).data

    def get_num_unresolved_alerts(self, node: models.Node) -> int:
        """Get the number of unresolved alerts for this node."""
        return node.alerts.filter(resolved=False).count()

    def get_upload_speed(self, node: models.Node) -> float | None:
        """Get node's upload speed."""
        return node.get_upload_speed()

    def get_download_speed(self, node: models.Node) -> float | None:
        """Get node's download speed."""
        return node.get_download_speed()
