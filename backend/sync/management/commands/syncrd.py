from django.core.management.base import BaseCommand
from sync.radiusdesk.sync_db import run as sync_radiusdesk


class Command(BaseCommand):

    help = "Sync with the radiusdesk database"

    def handle(self, *args, **options):
        sync_radiusdesk()
