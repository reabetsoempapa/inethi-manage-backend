# permissions.py

from rest_framework.permissions import BasePermission
from jose import jwt, JWTError
from django.conf import settings


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
                    return True
            except jwt.JWTError as e:
                print(e)
                pass
        return False


class UserAttributes(BasePermission):
    def attributes(self, request):
        auth = request.headers.get('Authorization', None)
        if auth:
            token = auth.split()[1]
            try:
                # Decode the token
                attributes = {}
                key = settings.KEYCLOAK_PUBLIC_KEY
                decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience='account')
                username = decoded_token.get('preferred_username', None)
                attributes['username'] = username
                roles = decoded_token.get('realm_access', {}).get('roles', [])
                attributes['create_wallet'] = False
                if 'wallet' in roles:
                    attributes['create_wallet'] = True
                return attributes
            except jwt.JWTError as e:
                print(e)
                return {
                    'username': '',
                    'create_wallet': False
                }
