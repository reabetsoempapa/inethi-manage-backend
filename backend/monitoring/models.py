from django.utils.functional import cached_property
from django.contrib.auth.models import User
from django.db import models
from macaddress.fields import MACAddressField

from metrics.models import ResourcesMetric, RTTMetric, DataRateMetric
from .checks import CheckResults


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

    class HealthStatus(models.TextChoices):
        """Health status choices."""

        UNKNOWN = "unknown", "Unknown"
        CRITICAL = "critical", "Critical"
        WARNING = "warning", "Warning"
        DECENT = "decent", "Decent"
        OK = "ok", "Ok"

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
    health_status = models.CharField(
        max_length=16, choices=HealthStatus.choices, default=HealthStatus.UNKNOWN
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

    def get_health_status(self) -> HealthStatus:
        """Convert CheckResults into health status."""
        if self.check_results.oll_korrect():
            return Node.HealthStatus.OK
        elif self.check_results.fewer_than_half_failed():
            return Node.HealthStatus.DECENT
        elif self.check_results.more_than_half_failed_but_not_all():
            return Node.HealthStatus.WARNING
        # All failed
        return Node.HealthStatus.CRITICAL

    def update_health_status(self, save: bool = True) -> None:
        """Run health checks and then update this node's health status."""
        self.health_status = self.get_health_status()
        if save:
            self.save(update_fields=["health_status"])

    def generate_alert(self) -> bool:
        """Generate an alert for this node, returns False if no alert is generated."""
        alert = Alert.from_node(self)
        if not alert:
            return False
        current_status_level = alert.level if alert else -1
        unresolved_alerts = Alert.objects.filter(node=self, resolved=False)
        # Only generate a new alert if the current state is worse than
        # that of an alert triggered last (or there are no previous alerts).
        # Otherwise we would be generating new alerts for the same state,
        # e.g. generating a WARNING alert for a node that has already got an
        # unresolved WARNING.
        if alert:
            latest_alert = unresolved_alerts.order_by("-created").first()
            # Case 1: There is no previous alert, so a new alert is generated
            # regardless of what the status may have been before
            if not latest_alert:
                alert.save()
            # Case 2: A new alert is generated because is is worse than the previous alerts 
            elif current_status_level > latest_alert.level:
                alert.save()
            # Case 3: The new report is as bad as previous ones, but may have
            # changed its reasons, so we generate a new one anyway.
            elif current_status_level == latest_alert.level and alert.text != latest_alert.text:
                alert.save()
        # Mark all previous alerts that were worse than the current status as resolved.
        # E.g. if a node generated a CRITICAL alert, but is now OK, that previous alert
        # is assumed to have been resolved.
        alerts_worse_than_current_status = unresolved_alerts.filter(level__gt=current_status_level)
        alerts_worse_than_current_status.update(resolved=True)
        return True

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

    class Level(models.IntegerChoices):
        """Alert level choices."""

        WARNING = 1, "Warning"
        ERROR = 2, "ERROR"
        CRITICAL = 3, "Critical"

    TITLE_OFFLINE = "Node is offline"
    TITLE_HEALTH_BAD = "Node's health is bad"
    TITLE_HEALTH_CRITICAL = "Node's health is critical"

    TEXT_OFFLINE = "The device is unreachable by ping"
    TEXT_HEALTH_BAD_OR_CRITICAL = "The following health checks failed: {}"

    level = models.SmallIntegerField(choices=Level.choices)
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="alerts")

    @classmethod
    def from_node(cls, node: Node) -> "Alert | None":
        """Generate an alert from a node's status."""
        if node.status == Node.Status.OFFLINE:
            return Alert(
                level=Alert.Level.WARNING,
                title=Alert.TITLE_OFFLINE,
                text=Alert.TEXT_OFFLINE,
                node=node,
            )
        if node.health_status != Node.HealthStatus.OK:
            health_checks_failed = ", ".join(
                c.key for c in node.check_results if not c.passed
            )
            if node.health_status == Node.HealthStatus.CRITICAL:
                return cls(
                    level=Alert.Level.CRITICAL,
                    title=Alert.TITLE_HEALTH_CRITICAL,
                    text=Alert.TEXT_HEALTH_BAD_OR_CRITICAL.format(health_checks_failed),
                    node=node,
                )
            if node.health_status in (
                Node.HealthStatus.WARNING,
                Node.HealthStatus.DECENT,
            ):
                return Alert(
                    level=Alert.Level.ERROR,
                    title=Alert.TITLE_HEALTH_BAD,
                    text=Alert.TEXT_HEALTH_BAD_OR_CRITICAL.format(health_checks_failed),
                    node=node,
                )
        return None

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
