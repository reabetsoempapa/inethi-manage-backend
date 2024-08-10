from typing import TYPE_CHECKING, Any
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from twilio.rest import Client

from . import models

logger = get_task_logger(__name__)


@shared_task
def send_alert_message(verb: str, alertId: int, meshName: str):
    """Send an alert SMS via Twilio."""
    if not settings.TWILIO_ENABLED:
        return 
    alert = models.Alert.objects.get(pk=alertId)
    mesh = models.Mesh.objects.get(name=meshName)
    levelName = models.Alert.Level(alert.level).label
    text = f"[{verb} {levelName}] {alert.title}\n{alert.text}"
    numbers = mesh.maintainers.values_list("profile__phone_number", flat=True)
    logger.info(f"Sending text to {meshName} ({numbers.count()} numbers)\n{text}")
    for phonenum in numbers:
        send_whatsapp(text, phonenum)


@shared_task
def send_whatsapp(body: str, number: str) -> None:
    """Send an sms from a twilio account."""
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_="whatsapp:+14155238886",
        body=body,
        to=f"whatsapp:{number}",
    )
    logger.debug("Sent message %s", message.sid)
