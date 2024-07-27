from django.utils.functional import cached_property
from django.contrib.auth.models import User
from django.db import models
from macaddress.fields import MACAddressField

from metrics.models import ResourcesMetric, RTTMetric, DataRateMetric
from .checks import CheckResults, CheckStatus


class WlanConf(models.Model):
    """Fireless configuration."""

    class Security(models.TextChoices):
        """Security mechanism for wireless access."""

        OPEN = "open", "Open"
        WPA_PSK = "wpapsk", "WPA-PSK"

    name = models.CharField(max_length=32)
    passphrase = models.CharField(max_length=100, null=True, blank=True)
    security = models.CharField(max_length=6, choices=Security.choices)
    is_guest = models.BooleanField(default=False)


class Mesh(models.Model):
    """Mesh consisting of nodes."""

    name = models.CharField(max_length=128, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    wlanconfs = models.ManyToManyField(WlanConf, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    lat = models.FloatField(default=0.0)
    lon = models.FloatField(default=0.0)


class Node(models.Model):
    """Database table for network devices."""

    class Hardware(models.TextChoices):
        """Hardware choices."""

        UBNT_AC_MESH = "ubnt_ac_mesh", "Ubiquiti AC Mesh"
        TP_LINK_EAP = "tl_eap225_3_o", "TPLink EAP"

    class Status(models.TextChoices):
        """Status choices."""

        UNKNOWN = "unknown", "Unknown"
        OFFLINE = "offline", "Offline"
        ONLINE = "online", "Online"
        REBOOTING = "rebooting", "Rebooting"

    # Required Fields
    mac = MACAddressField(primary_key=True)
    name = models.CharField(max_length=255)
    # Optional Fields
    mesh = models.ForeignKey(Mesh, on_delete=models.CASCADE, null=True, blank=True)
    adopted_at = models.DateTimeField(null=True, blank=True)
    last_contact = models.DateTimeField(null=True, blank=True)
    last_ping = models.DateTimeField(null=True, blank=True)
    is_ap = models.BooleanField(default=False)
    reachable = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.UNKNOWN
    )
    reboot_flag = models.BooleanField(default=False)
    neighbours = models.ManyToManyField("Node", blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    hardware = models.CharField(
        max_length=255, choices=Hardware.choices, default=Hardware.TP_LINK_EAP
    )
    ip = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def online(self) -> bool:
        """Check whether this node is online."""
        return self.status == Node.Status.ONLINE

    @online.setter
    def online(self, is_online: bool) -> None:
        """Set this node's online status."""
        self.status = Node.Status.ONLINE if is_online else Node.Status.OFFLINE

    @cached_property
    def last_rate_metric(self) -> DataRateMetric | None:
        """Get the last data rate metric for this node."""
        qs = DataRateMetric.objects.filter(
            mac=self.mac, tx_rate__isnull=False, rx_rate__isnull=False
        )
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


class ClientSession(models.Model):
    """A client session at a given access point."""

    mac = MACAddressField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    uplink = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="client_sessions"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    bytes_recv = models.IntegerField()
    bytes_sent = models.IntegerField()

    def __str__(self):
        return f"Client Session: {self.user.username}@{self.uplink} [{self.start_time}-{self.end_time}]"


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
        return cls(
            level=status.alert_level(),
            text=node.check_results.alert_summary(),
            node=node,
        )

    def type(self) -> str:
        """Alert type name."""
        return {3: "Critical", 2: "Warning", 1: "Decent", 0: "OK"}[self.level]

    def __str__(self):
        return f"Alert for {self.node} level={self.level} [{self.created}]"


class Service(models.Model):

    SERVICE_TYPES = (
        ("utility", "utility"),
        ("entertainment", "entertainment"),
        ("games", "games"),
        ("education", "education"),
    )

    API_LOCATIONS = (("cloud", "cloud"), ("local", "local"))

    url = models.URLField(max_length=100, unique=True)
    name = models.CharField(max_length=20, unique=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    api_location = models.CharField(max_length=10, choices=API_LOCATIONS)
