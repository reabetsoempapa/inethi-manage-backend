import logging
import time
import json
import zlib
import struct

from django.utils import timezone
from django.http import HttpRequest, HttpResponse
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from monitoring.models import Node
from sync.tasks import sync_device

logger = logging.getLogger(__file__)
last_contact = None
# TODO: AES-GCM key is hard-coded for now
aesgcm = AESGCM(bytes.fromhex("1d5f4f08478db1ab4b0caa05e3e65d11"))


def parse_inform(data: bytes) -> dict:
    """Parse data from the inform request."""
    headers, payload = data[:40], data[40:]
    magic, version, hardware, flags, iv, payload_version, payload_len = struct.unpack("!II6sh16sII", headers)
    assert magic == 1414414933 and payload_version == 1 and flags == 11
    decrypted = aesgcm.decrypt(iv, payload, headers)
    decompressed = zlib.decompress(decrypted)
    return json.loads(decompressed)


def hook_unifi_inform(request) -> None:
    """Hook calls by nodes to the unifi API."""
    global last_contact
    # Want to throttle this a little, by default unifi sends reports
    # every five seconds.
    if last_contact is not None and time.time() - last_contact < 60:
        return
    last_contact = time.time()
    data = parse_inform(request.body)
    node = Node.objects.filter(mac=data["mac"]).first()
    if node:
        node.last_contact = timezone.now()
        node.status = Node.Status.ONLINE
        node.save(update_fields=["last_contact", "status"])
        logger.info("Received report for %s", node.mac)
        sync_device.delay(str(node.mac))


def hook_unifi(
    request: HttpRequest,
    path: str,
    response: HttpResponse | None = None,
    hook_data=None,
) -> None:
    """Hook calls by nodes to the radiusdesk API."""
    if path == "inform":
        if response:
            pass
        else:
            return hook_unifi_inform(request)
