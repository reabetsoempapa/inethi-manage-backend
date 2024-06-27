import os

import requests
from rest_framework.views import APIView, Response
from rest_framework import status
from jose import jwt, JWTError, ExpiredSignatureError
from django.conf import settings
import logging
from dotenv import load_dotenv

# Get an instance of a logger
logger = logging.getLogger('general')
load_dotenv()
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
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

            if 'create_wallet' in roles:
                attributes['create_wallet'] = True
            return Response({'attributes': attributes}, status=status.HTTP_200_OK)
        except IndexError:
            logger.error("Authorization header is malformed.")
            return Response({"message": "Malformed Authorization header."}, status=status.HTTP_400_BAD_REQUEST)
        except ExpiredSignatureError:
            logger.error("Token has expired.")
            return Response({"message": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except JWTError as e:
            logger.error(f"JWT Error: {e}")
            return Response({"message": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterKeycloakUser(APIView):
    def post(self, request):
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')

        token_response = requests.post(
            'https://keycloak.inethicloud.net/realms/inethi-global-services/protocol/openid-connect/token', {
                'client_id': 'admin-cli',
                'client_secret': CLIENT_SECRET,
                'grant_type': 'client_credentials'
            })
        print(token_response.content)

        if token_response.status_code != 200:
            return Response({'error': 'Failed to authenticate with Keycloak'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token = token_response.json().get('access_token')
        print(access_token)
        # Register the user in Keycloak
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        user_data = {
            'username': username,
            'enabled': True,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            "emailVerified": False,
            'credentials': [{
                'type': 'password',
                'value': 'password',
                'temporary': False
            }]
        }

        registration_response = requests.post(
            'https://keycloak.inethicloud.net/admin/realms/inethi-global-services/users',
            json=user_data,
            headers=headers
        )
        print(registration_response.status_code)
        print(registration_response.content)

        if registration_response.status_code == 201:
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Failed to register user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
