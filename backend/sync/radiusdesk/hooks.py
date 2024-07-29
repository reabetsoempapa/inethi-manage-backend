from copy import deepcopy
import logging
import json

from django.utils import timezone
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from monitoring.models import Node
from sync.tasks import sync_device
from ..utils import get_src_ip

reports_logger = logging.getLogger("reports")
logger = logging.getLogger(__file__)


def hook_rd_report_request(request: HttpRequest) -> None:
    """Hook a request coming from a radiusdesk node to the server."""
    report = json.loads(request.body)
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
    node.ip = get_src_ip(request) or node.ip
    node.last_contact = timezone.now()
    node.status = Node.Status.ONLINE
    node.update_health_status(save=False)
    if report["report_type"] == "full":
        # TODO: Process full report
        pass
    node.save(update_fields=["is_ap", "last_contact", "status", "health_status", "ip"])
    # Generate an optional alert for this node based on the new status
    node.generate_alert()
    logger.info("Received report for %s", node.mac)
    return mac  # We need the mac when we process the response


def hook_rd_report_response(response: HttpResponse | StreamingHttpResponse, mac: str) -> None:
    """Hook a response from the radiusdesk server back to the node."""
    if isinstance(response, StreamingHttpResponse):
        response_data = json.loads(response.getvalue())
    else:
        response_data = json.loads(response.body)
    if response_data.get("success") and mac:
        node = Node.objects.filter(mac=mac).first()
        if node:
            # Allow our reboot_flag to also reboot nodes
            reboot_flag = response_data["reboot_flag"] or node.reboot_flag
            if reboot_flag:
                # We're about to send the reboot flag back to the node, we can reset it now
                node.reboot_flag = False
                node.status = Node.Status.REBOOTING
                node.save(update_fields=["reboot_flag", "status"])
            response_data["reboot_flag"] = reboot_flag
        sync_device.delay(str(node.mac))
    content = json.dumps(response_data, cls=DjangoJSONEncoder)
    # Patch the response content
    if isinstance(response, StreamingHttpResponse):
        response.streaming_content = [content]
    else:
        response.content = content


def hook_rd(
    request: HttpRequest,
    path: str,
    response: HttpResponse | None = None,
    hook_data=None,
) -> None:
    """Hook calls by nodes to the radiusdesk API."""
    if path == "cake4/rd_cake/nodes/get-config-for-node.json":
        pass
    elif path == "cake4/rd_cake/node-reports/submit_report.json":
        if response:
            return hook_rd_report_response(response, hook_data)
        else:
            return hook_rd_report_request(request)
    elif path == "cake4/rd_cake/node-actions/get_actions_for.json":
        pass
