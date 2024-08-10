from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from twilio.rest import Client

from . import models

logger = get_task_logger(__name__)


@shared_task
def send_alert_message(alertId: int):
    """Send an alert SMS via Twilio."""
    if not settings.TWILIO_ENABLED:
        return
    if not (
        settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
        and settings.TWILIO_PHONE_NUM
    ):
        logger.warning("Skipping alert messgae, Twilio not configured")
        return
    alert = models.Alert.objects.get(pk=alertId)
    if not alert.mesh:
        logger.error("Cannot send alert, alert is not associated with a mesh")
        return
    text = alert.message()
    numbers = alert.mesh.maintainers.values_list("profile__phone_number", flat=True)
    for phonenum in numbers:
        send_whatsapp(text, phonenum)


@shared_task
def send_whatsapp(body: str, number: str) -> None:
    """Send an sms from a twilio account."""
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_=f"whatsapp:{settings.TWILIO_PHONE_NUM}",
        body=body,
        to=f"whatsapp:{number}",
    )
    logger.debug("Sent message %s", message.sid)
