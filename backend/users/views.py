from rest_framework.views import APIView, Response
from rest_framework import status
from jose import jwt, JWTError, ExpiredSignatureError
from django.conf import settings
import logging

# Get an instance of a logger
logger = logging.getLogger('general')


class UserKeycloakAttributes(APIView):
    def get(self, request):
        if 'Authorization' not in request.headers:
            return Response({"status": "error", 'message': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        auth = request.headers.get('Authorization', None)
        token = auth.split()[1]
        try:
            attributes = {}
            key = settings.KEYCLOAK_PUBLIC_KEY
            decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience='account')
            username = decoded_token.get('preferred_username', None)
            attributes['username'] = username
            roles = decoded_token.get('realm_access', {}).get('roles', [])
            attributes['create_wallet'] = False
            if 'wallet' in roles:
                attributes['create_wallet'] = True
            return Response({'attributes': attributes}, status=status.HTTP_200_OK)
        except IndexError:
            logger.error("Authorization header is malformed.")
            return Response({"detail": "Malformed Authorization header."}, status=status.HTTP_400_BAD_REQUEST)
        except ExpiredSignatureError:
            logger.error("Token has expired.")
            return Response({"detail": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except JWTError as e:
            logger.error(f"JWT Error: {e}")
            return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
