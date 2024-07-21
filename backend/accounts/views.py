
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.contrib.auth.models import User

from . import serializers


class UserViewSet(ReadOnlyModelViewSet):
    """View User items."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
