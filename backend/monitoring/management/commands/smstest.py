from django.core.management.base import BaseCommand

from accounts.models import UserProfile
from monitoring.tasks import send_whatsapp


class Command(BaseCommand):

    help = "Send a test sms to all users."

    def handle(self, *args, **options):
        numbers = UserProfile.objects.values_list("phone_number", flat=True)
        for n in numbers:
            send_whatsapp("Hello there this is a test message", n)
