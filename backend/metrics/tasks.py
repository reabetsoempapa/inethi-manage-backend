from datetime import datetime, timedelta
import time
from typing import Type
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from monitoring.models import Node
from .models import UptimeMetric, RTTMetric, Metric
from .ping import ping

logger = get_task_logger(__name__)


@shared_task
def run_pings():
    for device in Node.objects.filter(ip__isnull=False):
        try:
            ping_data = ping(device.ip)
            reachable = ping_data["reachable"]
        except ValueError:
            reachable = False
        # If the ping failed the device is offline
        if not reachable:
            device.status = Node.Status.OFFLINE
        else:
            # Otherwise log the time of the last successful ping. Not that a
            # successful ping is not a guarantee that the node is online, it
            # has to send the server a report first.
            device.last_ping = timezone.now()
        # Update the device reachable status
        device.reachable = reachable
        device.save(update_fields=["reachable", "last_ping", "status"])
        rtt_data = ping_data.pop("rtt", None)
        UptimeMetric.objects.create(mac=device.mac, **ping_data)
        if rtt_data:
            RTTMetric.objects.create(mac=device.mac, **rtt_data)
        logger.info(f"PING {device.ip}")


def aggregate_metrics(metric_type: Type[Metric], to_gran: Metric.Granularity) -> None:
    """Aggregate metrics for a given metric type."""
    from_gran = to_gran.prev_granularity()
    from_gran_name = from_gran.name if from_gran else "None"
    metrics = metric_type.objects.filter(granularity=from_gran)
    old_metrics_count = metrics.count()
    first_metric, last_metric = metrics.last(), metrics.first()
    # Fewer than one of these metrics
    if not (first_metric and last_metric):
        logger.info("No %s metrics to aggregate, skipping", from_gran_name)
        return
    min_time = int(last_metric.created.timestamp())
    # For example, if we're going from HOURLY to DAILY we want to find
    # all of the hourly metrics from the beginning until one day ago.
    # The hourly metrics from the last day can remain as hourly metrics.
    max_time = int((timezone.now() - timedelta(seconds=to_gran.value)).timestamp())
    new_metrics_count = 0
    # HISTOGRAM
    # Bucket interval is the dest granularity's total_seconds
    for t0_int in range(min_time, max_time, to_gran.value):
        t0 = datetime.fromtimestamp(t0_int, tz=last_metric.created.tzinfo)
        t1 = t0 + timedelta(seconds=to_gran.value)
        ta = t0 + (t1 - t0) / 2
        # These are the old metrics that are going to be aggregated
        bucket_metrics = metrics.filter(created__gte=t0, created__lt=t1)
        # Group by mac address
        unique_mac_addresses = set(bucket_metrics.values_list("mac", flat=True))
        for mac in unique_mac_addresses:
            old_metrics = bucket_metrics.filter(mac=mac)
            old_metrics.create_aggregated(mac=mac, created=ta, granularity=to_gran)
            old_metrics.delete()
            new_metrics_count += 1
    logger.info(
        "Aggregated %d -> %d metrics for %s from %s to %s",
        old_metrics_count,
        new_metrics_count,
        metric_type.__name__,
        from_gran_name,
        to_gran.name,
    )


def aggregate_all_metrics(to_gran: Metric.Granularity) -> None:
    """Aggregate metrics for each metric type."""
    start_time = time.time()
    for metric_type in Metric.__subclasses__():
        aggregate_metrics(metric_type, to_gran)
    elapsed_time = timedelta(seconds=time.time() - start_time)
    logger.info("Aggregated %s metrics in %s", to_gran.name, elapsed_time)


@shared_task
def aggregate_all_hourly_metrics():
    """Aggregate to hourly metrics once an hour."""
    aggregate_all_metrics(Metric.Granularity.HOURLY)


@shared_task
def aggregate_all_daily_metrics():
    """Aggregate to daily metrics once a day."""
    aggregate_all_metrics(Metric.Granularity.DAILY)


@shared_task
def aggregate_all_monthly_metrics():
    """Aggregate to monthly metrics once a month."""
    aggregate_all_metrics(Metric.Granularity.MONTHLY)
