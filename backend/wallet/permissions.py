from rest_framework import permissions


class IsMyWalletOrReadOnly(permissions.BasePermission):
    """Allows edits when modifying the logged-in user's wallet."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_anonymous:
            return False
        if not hasattr(request.user, "wallet"):
            return False
        # Instance must be the logged in user
        return obj == request.user.wallet
