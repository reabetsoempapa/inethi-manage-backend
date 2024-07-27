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
    node.status = Node.Status.ONLINE
    if report["report_type"] == "full":
        # TODO: Process full report
        pass
    node.save(update_fields=["is_ap", "last_contact", "status"])
    logger.info("Received report for %s", node.mac)


def hook_report_response(response_data: dict, request) -> dict:
    """Allow modifying the request from the radiusdesk server."""
    if response_data.get("success"):
        node = Node.objects.filter(mac=request.data["mac"]).first()
        if not node:
            sync_device.delay(str(node.mac))
            return response_data
        # Allow our reboot_flag to also reboot nodes
        reboot_flag = response_data["reboot_flag"] or node.reboot_flag
        if reboot_flag:
            # We're about to send the reboot flag back to the node, we can reset it now
            node.reboot_flag = False
            node.status = Node.Status.REBOOTING
            node.save(update_fields=["reboot_flag", "status"])
        response_data["reboot_flag"] = reboot_flag
    sync_device.delay(str(node.mac))
    return response_data
