from django.core.management.base import BaseCommand
from monitoring.sync.radiusdesk import run as sync_radiusdesk


class Command(BaseCommand):

    help = "Sync with the radiusdesk database"

    def handle(self, *args, **options):
        sync_radiusdesk()