from celery import shared_task
from celery.utils.log import get_task_logger

from monitoring.models import Node
from .models import UptimeMetric, RTTMetric
from .ping import ping

logger = get_task_logger(__name__)


@shared_task
def run_pings():
    for device in Node.objects.filter(ip__isnull=False):
        try:
            ping_data = ping(device.ip)
            is_online = ping_data["reachable"]
        except ValueError:
            is_online = False
        # Update the device online status
        if device.online != is_online:
            device.online = is_online
            device.save(update_fields=["online"])
        rtt_data = ping_data.pop("rtt", None)
        UptimeMetric.objects.create(mac=device.mac, **ping_data)
        if rtt_data:
            RTTMetric.objects.create(mac=device.mac, **rtt_data)
        logger.info(f"PING {device.ip}")
