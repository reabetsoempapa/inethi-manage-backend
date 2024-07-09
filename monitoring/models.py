from datetime import datetime
from django.utils.functional import cached_property
from django.db import models
from macaddress.fields import MACAddressField

from metrics.models import UptimeMetric, ResourcesMetric, RTTMetric, DataRateMetric
from .checks import CheckResults, CheckStatus


class Mesh(models.Model):
    """Mesh consisting of nodes."""

    name = models.CharField(max_length=128, primary_key=True)
    ssid = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now_add=True)


class Node(models.Model):
    """Database table for network devices."""

    # Required Fields
    mac = MACAddressField(primary_key=True)
    name = models.CharField(max_length=255)
    mesh = models.ForeignKey(Mesh, on_delete=models.CASCADE)
    # Optional Fields
    online = models.BooleanField(default=False)
    neighbours = models.ManyToManyField("Node", blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    hardware = models.CharField(max_length=255, blank=True, null=True)
    ip = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    @cached_property
    def last_uptime_metric(self) -> UptimeMetric | None:
        """Get the last uptime metric for this node."""
        qs = UptimeMetric.objects.filter(mac=self.mac, reachable=True)
        return qs.order_by("-created").first()

    @cached_property
    def last_rate_metric(self) -> DataRateMetric | None:
        """Get the last data rate metric for this node."""
        qs = DataRateMetric.objects.filter(mac=self.mac, tx_rate__isnull=False, rx_rate__isnull=False)
        return qs.order_by("-created").first()

    @cached_property
    def last_resource_metric(self) -> ResourcesMetric | None:
        """Get the last resource for this node."""
        return ResourcesMetric.objects.filter(mac=self.mac).order_by("-created").first()

    @cached_property
    def last_rtt_metric(self) -> RTTMetric | None:
        """Get the last RTT for this node."""
        return RTTMetric.objects.filter(mac=self.mac).order_by("-created").first()

    @cached_property
    def check_results(self) -> CheckResults:
        """Get new or cached check results for this node."""
        return CheckResults.run_checks(self)

    def get_is_contacted(self) -> bool | None:
        """Get device contacted status."""
        return self.last_uptime_metric is not None

    def get_last_contacted_time(self) -> datetime | None:
        """Get this time that this node was last contacted."""
        return getattr(self.last_uptime_metric, "created", None)

    def get_cpu(self) -> bool | None:
        """Get device CPU usage."""
        return getattr(self.last_resource_metric, "cpu", None)

    def get_mem(self) -> bool | None:
        """Get device memory usage."""
        return getattr(self.last_resource_metric, "memory", None)

    def get_rtt(self) -> bool | None:
        """Get device RTT time."""
        return getattr(self.last_rtt_metric, "rtt_avg", None)

    def get_download_speed(self) -> float | None:
        """Get device download speed."""
        return getattr(self.last_rate_metric, "tx_rate", None)

    def get_upload_speed(self) -> float | None:
        """Get device upload speed."""
        return getattr(self.last_rate_metric, "rx_rate", None)

    def __str__(self):
        return f"Node {self.name} ({self.mac})"


class UnknownNode(models.Model):
    """Nodes that haven't been adopted yet."""

    mac = MACAddressField(primary_key=True)
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=15)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Unknown Node {self.mac} [{self.created}]"


class Service(models.Model):
    """Database table for services."""

    SERVICE_TYPES = (
        ("utility", "Utility"),
        ("entertainment", "Entertainment"),
        ("games", "Games"),
        ("education", "Education"),
    )

    API_LOCATIONS = (("cloud", "Cloud"), ("local", "Local"))

    url = models.URLField(max_length=100, unique=True)
    name = models.CharField(max_length=20, unique=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    api_location = models.CharField(max_length=10, choices=API_LOCATIONS)


class Alert(models.Model):
    """Alert sent to network managers."""

    ALERT_LEVELS = (
        (3, "Critical"),
        (2, "Warning"),
        (1, "Decent"),
        (0, "OK"),
    )

    level = models.SmallIntegerField(choices=ALERT_LEVELS)
    text = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="alerts")

    @classmethod
    def from_status(cls, node: Node, status: CheckStatus) -> "Alert":
        """Generate an alert from a node's status."""
        return cls(level=status.alert_level(),
                   text=node.check_results.alert_summary(),
                   node=node)

    def type(self) -> str:
        """Alert type name."""
        return {
            3: "Critical",
            2: "Warning",
            1: "Decent",
            0: "OK"
        }[self.level]

    def __str__(self):
        return f"Alert for {self.node} level={self.level} [{self.created}]"
