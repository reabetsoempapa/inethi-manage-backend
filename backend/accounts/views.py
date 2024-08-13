import json
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import transaction
from django_keycloak.tools import create_keycloak_user
from keycloak.exceptions import KeycloakError

from .permissions import IsRequestUserOrReadOnly, IsCreationOrIsAuthenticated
from . import serializers


class UserViewSet(ModelViewSet):
    """View User items."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    lookup_value_regex = "[0-9]*|current"
    permission_classes = [IsRequestUserOrReadOnly, IsCreationOrIsAuthenticated]

    def perform_authentication(self, request):
        """Replace 'current' pk with the request user's pk."""
        super().perform_authentication(request)
        if self.kwargs.get("pk") == "current":
            self.kwargs["pk"] = request.user.id

    def perform_create(self, serializer: serializers.UserSerializer):
        """Create a keycloak user after creating a django user."""
        try:
            with transaction.atomic():
                # 1. Create the django user
                user = serializer.save()
                # 2. Create the keycloak user
                create_keycloak_user(user, serializer.validated_data["password"])
        except KeycloakError as ke:
            # Will be handled by DRF's error handler
            try:
                msg = json.loads(ke.error_message).get("errorMessage")
            except json.JSONDecodeError:
                msg = ke.error_message
            raise ValidationError(msg) from ke

    def update(self, request, *args, **kwargs):
        # Bit of a pain, but seems like nested updates to one-to-one fields don't
        # work so lekker. I've more or less re-implemented the functionality in the
        # uper().update method, but saving the profile first before saving the user data.
        user = self.get_object()
        profile_data = request.data.pop("profile", None)
        if profile_data:
            profile_serializer = serializers.UserProfileSerializer(
                user.profile, data=profile_data, context=self.get_serializer_context()
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
        return super().update(request, *args, **kwargs)
