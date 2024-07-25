from django.core.management.base import BaseCommand
from sync.unifi.sync_db import run as sync_unifi


class Command(BaseCommand):

    help = "Sync with the unifi database"

    def handle(self, *args, **options):
        sync_unifi()
