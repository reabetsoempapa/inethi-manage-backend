from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Mesh, MeshSettings


@receiver(post_save, sender=Mesh)
def create_settings_if_not_defined(sender, created, instance, **kwargs):
    """Update prometheus targets when network devices are added or modified."""
    if created:
        MeshSettings.objects.create(mesh=instance, **settings.MESH_SETTINGS_DEFAULTS)
