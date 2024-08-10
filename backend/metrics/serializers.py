from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField

from . import models


class UptimeMetricSerializer(ModelSerializer):
    """Serializes UptimeMetric objects from django model to JSON."""

    node = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """UptimeMetricSerializer metadata."""

        model = models.UptimeMetric
        fields = "__all__"


class FailuresMetricSerializer(ModelSerializer):
    """Serializes FailuresMetric objects from django model to JSON."""

    class Meta:
        """FailuresMetricSerializer metadata."""

        model = models.FailuresMetric
        fields = "__all__"

    tx_retries_perc = SerializerMethodField()

    def get_tx_retries_perc(self, obj: models.FailuresMetric):
        """Get tx_retries as a percentage."""
        if obj.tx_packets == 0:
            return 0
        return round(obj.tx_retries / obj.tx_packets * 100)


class ResourcesMetricSerializer(ModelSerializer):
    """Serializes ResourcesMetric objects from django model to JSON."""

    class Meta:
        """ResourcesMetricSerializer metadata."""

        model = models.ResourcesMetric
        fields = "__all__"


class RTTMetricSerializer(ModelSerializer):
    """Serializes RTTMetric objects from django model to JSON."""

    class Meta:
        """RTTMetricSerializer metadata."""

        model = models.RTTMetric
        fields = "__all__"


class DataUsageMetricSerializer(ModelSerializer):
    """Serializes DataUsageMetric objects from django model to JSON."""

    class Meta:
        """DataUsageMetricSerializer metadata."""

        model = models.DataUsageMetric
        fields = "__all__"


class DataRateMetricSerializer(ModelSerializer):
    """Serializes DataRateMetric objects from django model to JSON."""

    class Meta:
        """DataRateMetricSerializer metadata."""

        model = models.DataRateMetric
        fields = "__all__"
