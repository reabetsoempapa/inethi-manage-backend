from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Mesh, MeshSettings, Alert
from .tasks import send_alert_message


@receiver(post_save, sender=Mesh)
def create_settings_if_not_defined(sender, created, instance, **kwargs):
    """Create mesh settings for a new mesh."""
    if created:
        MeshSettings.objects.create(mesh=instance, **settings.MESH_SETTINGS_DEFAULTS)


@receiver(post_save, sender=Alert)
def send_message_on_alert_save(sender, created, instance, **kwargs):
    """Send a whatsapp message after creating or modifying alerts."""
    send_alert_message.delay(instance.pk)
