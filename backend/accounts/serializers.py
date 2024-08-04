from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework.serializers import ModelSerializer, SerializerMethodField, SlugRelatedField

from radius.models import Radacct


class UserSerializer(ModelSerializer):
    """Serializes User objects from django model to JSON."""

    num_sessions = SerializerMethodField()
    bytes_recv = SerializerMethodField()
    bytes_sent = SerializerMethodField()
    groups = SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        """UserSerializer metadata."""

        model = User
        exclude = ("password",)
        
    def sessions(self, user: User):
        return Radacct.objects.filter(username=user.username)

    def get_num_sessions(self, user: User) -> int:
        return self.sessions(user).count()

    def get_bytes_recv(self, user: User) -> int:
        return self.sessions(user).aggregate(Sum("acctinputoctets"))["acctinputoctets__sum"]

    def get_bytes_sent(self, user: User) -> int:
        return self.sessions(user).aggregate(Sum("acctoutputoctets"))["acctoutputoctets__sum"]
