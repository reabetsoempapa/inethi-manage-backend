"""Sync with a radiusdesk database."""

import time
from datetime import datetime

from pymongo import MongoClient
from django.conf import settings
from django.utils.timezone import make_aware
import pytz

from monitoring.models import Mesh, Node
from metrics.models import DataUsageMetric, FailuresMetric, ResourcesMetric, DataRateMetric
from .utils import bulk_sync

TZ = pytz.UTC


@bulk_sync(Mesh)
def sync_meshes(client):
    """Sync Mesh objects from the unifi database."""
    for site in client.ace.site.find():
        yield {}, {"name": site["name"]}


@bulk_sync(Node, delete=False)
def sync_nodes(client):
    """Sync Node objects from the unifi database."""
    for device in client.ace.device.find():
        adoption_details = client.ace.event.find_one({"key": "EVT_AP_Adopted", "ap": device["mac"]})
        name = adoption_details["ap_name"] if adoption_details else device["model"]
        adopt_time = make_aware(datetime.fromtimestamp(device["adopted_at"] / 1e3), TZ)
        data = dict(
            mesh=Mesh.objects.get(name=device["last_connection_network_name"].lower()),
            name=name,
            description="",
            mac=device["mac"],
            hardware=device["model"],
            ip=device["ip"],
            created=adopt_time,
        )
        yield data, {"mac": device["mac"]}


@bulk_sync(DataUsageMetric)
def sync_node_data_usage_metrics(client):
    """Sync DataUsageMetric objects from the unifi database."""
    aps = client.ace_stat.stat_hourly.find({"o": "ap"})
    for ap in aps:
        ap_time = make_aware(datetime.fromtimestamp(ap["time"] / 1e3), TZ)
        data = dict(
            mac=ap["ap"],
            tx_bytes=ap.get("tx_bytes"),
            rx_bytes=ap.get("rx_bytes"),
        )
        yield data, {"created": ap_time}


@bulk_sync(DataRateMetric)
def sync_node_data_rate_metrics(client):
    """Sync DataRateMetric objects from the unifi database."""
    aps = client.ace_stat.stat_5minutes.find({"o": "ap"})
    for ap in aps:
        ap_time = make_aware(datetime.fromtimestamp(ap["time"] / 1e3), TZ)
        bytes_per_5mins_to_bits_per_second = 8 / 5 / 60
        data = dict(
            mac=ap["ap"],
            tx_rate=ap.get("client-tx_bytes") * bytes_per_5mins_to_bits_per_second,
            rx_rate=ap.get("client-rx_bytes") * bytes_per_5mins_to_bits_per_second,
        )
        yield data, {"created": ap_time}


@bulk_sync(FailuresMetric)
def sync_node_failures_metrics(client):
    """Sync FailuresMetric objects from the unifi database."""
    aps = client.ace_stat.stat_hourly.find({"o": "ap"})
    for ap in aps:
        ap_time = make_aware(datetime.fromtimestamp(ap["time"] / 1e3), TZ)
        data = dict(
            mac=ap["ap"],
            tx_packets=ap.get("tx_packets"),
            rx_packets=ap.get("rx_packets"),
            tx_dropped=ap.get("tx_dropped"),
            rx_dropped=ap.get("rx_dropped"),
            tx_errors=ap.get("tx_failed"),
            rx_errors=ap.get("rx_failed"),
            tx_retries=ap.get("tx_retries"),
        )
        yield data, {"created": ap_time}


@bulk_sync(ResourcesMetric)
def sync_node_resources_metrics(client):
    """Sync NodeLoad objects from the unifi database."""
    aps = client.ace_stat.stat_hourly.find({"o": "ap"})
    for ap in aps:
        ap_time = make_aware(datetime.fromtimestamp(ap["time"] / 1e3), TZ)
        data = dict(
            mac=ap["ap"],
            memory=ap.get("mem"),
            cpu=ap.get("cpu"),
        )
        yield data, {"created": ap_time}


def run():
    _client = MongoClient(
        host=settings.UNIFI_DB_HOST,
        port=int(settings.UNIFI_DB_PORT),
        username=settings.UNIFI_DB_USER,
        password=settings.UNIFI_DB_PASSWORD,
    )
    start_time = time.time()
    sync_meshes(_client)
    sync_nodes(_client)
    sync_node_data_usage_metrics(_client)
    sync_node_data_rate_metrics(_client)
    sync_node_failures_metrics(_client)
    sync_node_resources_metrics(_client)
    elapsed_time = time.time() - start_time
    print(f"Synced with unifi in {elapsed_time:.2f}s")
