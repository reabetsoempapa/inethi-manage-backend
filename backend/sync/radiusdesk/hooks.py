from copy import deepcopy
import logging
import json

logger = logging.getLogger("reports")


def hook_reports(report: dict) -> None:
    """Hook calls by nodes to the radiusdesk API."""
    # This little deepcopy bug wasted FOUR AND A HALF HOURS of my life :)
    report_copy = deepcopy(report)
    logger.info("%s %s", report_copy.pop("mac"), json.dumps(report_copy))
