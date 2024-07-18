from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class UserSerializer(ModelSerializer):
    """Serializes User objects from django model to JSON."""

    num_sessions = SerializerMethodField()
    bytes_recv = SerializerMethodField()
    bytes_sent = SerializerMethodField()

    class Meta:
        """UserSerializer metadata."""

        model = User
        exclude = ("password",)

    def get_num_sessions(self, user: User) -> int:
        return user.sessions.count()

    def get_bytes_recv(self, user: User) -> int:
        return user.sessions.aggregate(Sum("bytes_recv"))["bytes_recv__sum"]

    def get_bytes_sent(self, user: User) -> int:
        return user.sessions.aggregate(Sum("bytes_sent"))["bytes_sent__sum"]
