from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User

from .permissions import IsRequestUserOrReadOnly
from . import serializers


class UserViewSet(ModelViewSet):
    """View User items."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    lookup_value_regex = "[0-9]*|current"
    permission_classes = [IsRequestUserOrReadOnly]

    def perform_authentication(self, request):
        """Replace 'current' pk with the request user's pk."""
        super().perform_authentication(request)
        if self.kwargs.get("pk") == "current":
            self.kwargs["pk"] = request.user.id

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
