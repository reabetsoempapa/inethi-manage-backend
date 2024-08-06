from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
import channels.layers
from django.conf import settings

from sync.radiusdesk.sync_db import run as syncrd
from sync.unifi.sync_db import run as syncunifi
from monitoring.models import Node
from monitoring.serializers import NodeSerializer

logger = get_task_logger(__name__)


@shared_task
def sync_dbs() -> None:
    """Sync with radiusdesk and unifi, then update devices."""
    synced = False
    if settings.SYNC_RD_ENABLED:
        logger.info("Syncing with radiusdesk")
        syncrd()
        synced = True
    if settings.SYNC_UNIFI_ENABLED:
        logger.info("Syncing with unifi")
        syncunifi()
        synced = True
    if synced:
        sync_all_devices()


@shared_task
def generate_alerts(node_mac: str | None = None) -> None:
    """Generate alerts for all nodes."""
    logger.info("Generating alerts")
    node = Node.objects.get(mac=node_mac) if node_mac else None
    for n in ([node] if node else Node.objects.all()):
        n.generate_alert()


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
