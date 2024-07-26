import logging
import time

from django.utils import timezone

from monitoring.models import Node
from sync.tasks import sync_device
from .parsers import InformParser

logger = logging.getLogger(__file__)
last_contact = None


def hook_inform(encrypted_data: dict) -> None:
    """Hook calls by nodes to the unifi API."""
    global last_contact
    # Want to throttle this a little, by default unifi sends reports
    # every five seconds.
    if last_contact is not None and time.time() - last_contact < 60:
        return
    last_contact = time.time()
    data = InformParser.parse_inform(encrypted_data)
    node = Node.objects.filter(mac=data["mac"]).first()
    if node:
        node.last_contact = timezone.now()
        node.save(update_fields=["last_contact"])
        logger.info("Received report for %s", node.mac)
        sync_device.delay(str(node.mac))
