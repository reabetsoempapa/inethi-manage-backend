# permissions.py

from rest_framework.permissions import BasePermission
from jose import jwt
from django.conf import settings
import logging

# Get an instance of a logger
logger = logging.getLogger('general')


class IsAdminUser(BasePermission):
    message = "Access denied. User must be an admin."

    def has_permission(self, request, view):
        # Extract the token from the Authorization header
        auth = request.headers.get('Authorization', None)
        if auth:
            token = auth.split()[1]
            try:
                # Decode the token
                key = settings.KEYCLOAK_PUBLIC_KEY
                decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience='account')

                roles = decoded_token.get('realm_access', {}).get('roles', [])
                if 'admin' in roles:
                    logging.info(f"Admin user accessing a service: {decoded_token}")
                    return True
                else:
                    logging.info(f"Non-admin user attempted to access a protected service a service: {decoded_token}")
            except jwt.JWTError as e:
                logging.error(f"Cannot authenticate user as admin: {e}")
                pass
        return False

