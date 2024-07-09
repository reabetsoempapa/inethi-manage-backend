from django.db import models
from django.utils import timezone
from macaddress.fields import MACAddressField


class Metric(models.Model):
    """Base class for Metric objects."""

    class Meta:
        """Metric metadata."""

        ordering = ["created"]

    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = timezone.now()
        super().save(*args, **kwargs)

    created = models.DateTimeField()
    mac = MACAddressField()


class ResourcesMetric(Metric):
    """Metric for system resources (memor, cpu usage)."""

    memory = models.FloatField()
    cpu = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Metric: Resources [{self.created}]"


class UptimeMetric(Metric):
    """Metric for uptime, gathered during periodic pings."""

    reachable = models.BooleanField()
    loss = models.IntegerField()

    def __str__(self):
        return f"Metric: Uptime [{self.created}]"


class RTTMetric(Metric):
    """Metric for round trip time, gathered during periodic pings."""

    rtt_min = models.FloatField(null=True, blank=True)
    rtt_avg = models.FloatField(null=True, blank=True)
    rtt_max = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Metric: RTT [{self.created}]"


class DataUsageMetric(Metric):
    """Metric for a node's data usage."""

    tx_bytes = models.BigIntegerField()
    rx_bytes = models.BigIntegerField()

    def __str__(self):
        return f"Metric: Data Usage [{self.created}]"


class DataRateMetric(Metric):
    """Metric for a node's transfer/receive speed."""

    tx_rate = models.IntegerField(null=True, blank=True)
    rx_rate = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Metric: Data Rate [{self.created}]"


class FailuresMetric(Metric):
    """Metric for wifi failures."""

    tx_packets = models.BigIntegerField()
    rx_packets = models.BigIntegerField()
    tx_dropped = models.IntegerField(null=True, blank=True)
    rx_dropped = models.IntegerField(null=True, blank=True)
    tx_retries = models.IntegerField(null=True, blank=True)
    tx_errors = models.IntegerField(null=True, blank=True)
    rx_errors = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Metric: Failures [{self.created}]"
