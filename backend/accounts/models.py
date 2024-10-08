from django.db import models
from django.utils.functional import cached_property
from django.contrib.auth.models import User
from django.db.models import Sum
from phonenumber_field.modelfields import PhoneNumberField

from monitoring.models import Alert, Mesh
from radius.models import Radacct


class UserProfile(models.Model):
    """Extra data associated with a user."""

    alert_notifications_enabled = models.BooleanField(default=False)
    min_alert_level = models.SmallIntegerField(
        choices=Alert.Level.choices, default=Alert.Level.WARNING
    )
    alert_meshes = models.ManyToManyField(Mesh, related_name="alerted_users", blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = PhoneNumberField(blank=True)

    def __str__(self):
        return f"{self.user.username.capitalize()}'s Profile"

    @cached_property
    def sessions(self):
        """Get sessions started by this user."""
        return Radacct.objects.filter(username=self.user.username)

    @cached_property
    def num_sessions(self) -> int:
        """Get the number of sessions started by this user."""
        return self.sessions.count()

    @cached_property
    def bytes_recv(self) -> int:
        """Get total bytes received by this user."""
        return self.sessions.aggregate(Sum("acctinputoctets"))["acctinputoctets__sum"]

    @cached_property
    def bytes_sent(self) -> int:
        """Get total bytes sent by this user."""
        return self.sessions.aggregate(Sum("acctoutputoctets"))["acctoutputoctets__sum"]
