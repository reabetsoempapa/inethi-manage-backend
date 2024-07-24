
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User

from .permissions import IsRequestUserOrReadOnly
from . import serializers


class UserViewSet(ModelViewSet):
    """View User items."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    lookup_value_regex = '[0-9]*|current'
    permission_classes = [IsRequestUserOrReadOnly]

    def perform_authentication(self, request):
        """Replace 'current' pk with the request user's pk."""
        super().perform_authentication(request)
        if self.kwargs.get("pk") == "current":
            self.kwargs["pk"] = request.user.id
