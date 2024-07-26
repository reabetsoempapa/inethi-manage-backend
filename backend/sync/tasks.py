from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
import channels.layers

from sync.radiusdesk.sync_db import run as syncrd
from sync.unifi.sync_db import run as syncunifi
from monitoring.checks import CheckStatus
from monitoring.models import Node, Alert
from monitoring.serializers import NodeSerializer

logger = get_task_logger(__name__)


@shared_task
def sync_dbs() -> None:
    """Sync with radiusdesk and unifi, then update devices."""
    logger.info("Syncing with radiusdesk")
    syncrd()
    logger.info("Syncing with unifi")
    syncunifi()
    sync_all_devices()


@shared_task
def generate_alerts(node_mac: str | None = None) -> None:
    """Generate alerts for all nodes."""
    logger.info("Generating alerts")
    node = Node.objects.get(mac=node_mac) if node_mac else None
    for n in ([node] if node else Node.objects.all()):
        current_status = n.check_results.status()
        current_status_level = current_status.alert_level()
        unresolved_alerts = Alert.objects.filter(node=n, resolved=False)
        # Only generate a new alert if the current state is worse than
        # that of an alert triggered last (or there are no previous alerts).
        # Otherwise we would be generating new alerts for the same state,
        # e.g. generating a WARNING alert for a node that has already got an
        # unresolved WARNING.
        if current_status != CheckStatus.OK:
            latest_alert = unresolved_alerts.order_by("-created").first()
            if not latest_alert or current_status_level > latest_alert.level:
                # Generate the alert
                alert = Alert.from_status(n, current_status)
                alert.save()
                logger.info("Generated an alert for %s: %s", n, alert)
        # Mark all previous alerts that were worse than the current status as resolved.
        # E.g. if a node generated a CRITICAL alert, but is now OK, that previous alert
        # is assumed to have been resolved.
        alerts_worse_than_current_status = unresolved_alerts.filter(level__gt=current_status_level)
        alerts_worse_than_current_status.update(resolved=True)


@shared_task
def sync_device(device_mac: str) -> None:
    """Sync a specific device and send an update via channels."""
    logger.info("Syncing device %s", device_mac)
    device = Node.objects.filter(mac=device_mac).first()
    if not device:
        logger.error("No device with MAC %s", device_mac)
        return
    serializer = NodeSerializer(device)
    logger.info("%s %s", device.last_contact, serializer.data["last_contact"])
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)('updates_group', {
        "type": "update.device",
        "data": serializer.data
    })


@shared_task
def sync_all_devices() -> None:
    """Sync all devices, then send an update via channels."""
    logger.info("Syncing devices")
    serializer = NodeSerializer(Node.objects.all(), many=True)
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)('updates_group', {
        "type": "update.devices",
        "data": serializer.data
    })
