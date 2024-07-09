from datetime import datetime
from rest_framework.viewsets import ModelViewSet

from . import models
from . import serializers


class FilterByDeviceMacMixin:
    """Allow filtering a view's query set for a particular node."""

    MAC_FIELD = "mac"

    def filter_queryset(self, qs):
        """Filter against a 'mac' parameter in the request query."""
        qs = super().filter_queryset(qs)
        mac = self.request.query_params.get(self.MAC_FIELD)
        if mac is not None:
            qs = qs.filter(mac=mac)
        return qs


class FilterByMinTimeMixin:
    """Allow filtering a view's query set on a particular min time range."""

    MIN_TIME_FIELD = "min_time"

    def filter_queryset(self, qs):
        """Filter against a 'min_time' parameter in the request query."""
        qs = super().filter_queryset(qs)
        min_time = self.request.query_params.get(self.MIN_TIME_FIELD)
        if not min_time:
            return qs
        try:
            min_time_int = int(min_time)
        except ValueError:
            return qs
        return qs.filter(created__gt=datetime.fromtimestamp(min_time_int))


class UptimeViewSet(FilterByMinTimeMixin, FilterByDeviceMacMixin, ModelViewSet):
    """View/Edit/Add/Delete UptimeMetric items."""

    queryset = models.UptimeMetric.objects.all()
    serializer_class = serializers.UptimeMetricSerializer


class FailuresViewSet(FilterByMinTimeMixin, FilterByDeviceMacMixin, ModelViewSet):
    """View/Edit/Add/Delete FailuresMetric items."""

    queryset = models.FailuresMetric.objects.all()
    serializer_class = serializers.FailuresMetricSerializer


class RTTViewSet(FilterByMinTimeMixin, FilterByDeviceMacMixin, ModelViewSet):
    """View/Edit/Add/Delete RTTMetric items."""

    queryset = models.RTTMetric.objects.all()
    serializer_class = serializers.RTTMetricSerializer


class ResourcesViewSet(FilterByMinTimeMixin, FilterByDeviceMacMixin, ModelViewSet):
    """View/Edit/Add/Delete ResourcesMetric items."""

    queryset = models.ResourcesMetric.objects.all()
    serializer_class = serializers.ResourcesMetricSerializer


class DataUsageViewSet(FilterByMinTimeMixin, FilterByDeviceMacMixin, ModelViewSet):
    """View/Edit/Add/Delete DataUsageMetric items."""

    queryset = models.DataUsageMetric.objects.all()
    serializer_class = serializers.DataUsageMetricSerializer


class DataRateViewSet(FilterByMinTimeMixin, FilterByDeviceMacMixin, ModelViewSet):
    """View/Edit/Add/Delete DataRateMetric items."""

    queryset = models.DataRateMetric.objects.all()
    serializer_class = serializers.DataRateMetricSerializer
