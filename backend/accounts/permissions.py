from django.contrib.auth.models import User
from rest_framework import permissions


class IsRequestUserOrReadOnly(permissions.BasePermission):
    """Allows edits when modifying the logged-in user."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_anonymous:
            return False
        # Instance must be the logged in user
        return isinstance(obj, User) and obj.id == request.user.id
