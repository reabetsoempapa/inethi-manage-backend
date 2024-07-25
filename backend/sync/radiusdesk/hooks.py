import logging
import json

logger = logging.getLogger("reports")


def hook_reports(report: dict):
    logger.info(f'{report.pop("mac")} {json.dumps(report)}')
