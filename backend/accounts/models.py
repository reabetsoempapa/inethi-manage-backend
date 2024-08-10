from django.db import models
from django.utils.functional import cached_property
from django.contrib.auth.models import User
from django.db.models import Sum

from monitoring.models import Alert
from radius.models import Radacct


class UserProfile(models.Model):
    """Extra data associated with a user."""

    alert_notifications_enabled = models.BooleanField(default=False)
    min_alert_level = models.SmallIntegerField(
        choices=Alert.Level.choices, default=Alert.Level.WARNING
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

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
