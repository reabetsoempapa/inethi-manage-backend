from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes UserProfile objects from django model to JSON."""

    num_sessions = serializers.IntegerField(read_only=True)
    bytes_recv = serializers.IntegerField(read_only=True)
    bytes_sent = serializers.IntegerField(read_only=True)

    class Meta:
        """UserProfileSerializer metadata."""

        model = UserProfile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """Serializes User objects from django model to JSON."""

    profile = UserProfileSerializer(required=False)
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        """UserSerializer metadata."""

        model = User
        exclude = ("password",)
