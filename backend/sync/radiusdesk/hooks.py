from copy import deepcopy
import logging
import json

from django.utils import timezone

from monitoring.models import Node
from sync.tasks import sync_device

reports_logger = logging.getLogger("reports")
logger = logging.getLogger(__file__)


def hook_reports(report: dict) -> None:
    """Hook calls by nodes to the radiusdesk API."""
    # This little deepcopy bug wasted FOUR AND A HALF HOURS of my life :)
    # DON'T MODIFY DATA THAT'S GOING TO BE FORWARDED!!!!!
    report_copy = deepcopy(report)
    mac = report_copy.pop("mac")
    reports_logger.info("%s %s", mac, json.dumps(report_copy))
    node = Node.objects.filter(mac=mac).first()
    if not node:
        logger.warning("Received report for an unregistered node.")
        return
    # Both light and full reports send mode
    node.is_ap = report["mode"] == "ap"
    node.last_contact = timezone.now()
    # TODO: Process full report
    node.save()
    logger.info("Received report for %s", node.mac)
    sync_device.delay(str(node.mac))
