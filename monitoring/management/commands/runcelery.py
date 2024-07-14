from django.core.management.base import BaseCommand
from monitoring.tasks import run_sync
from metrics.tasks import run_pings


class Command(BaseCommand):

    help = "Run all celery tasks."

    def handle(self, *args, **options):
        run_pings.delay()
        # Small delay to prevent database locked errors with sqlite.
        run_sync.apply_async(args=(), countdown=2)
