from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import AppUser
from .serializers import AppUserSerializer
from jose import jwt, JWTError, ExpiredSignatureError
from django.conf import settings
import logging
import os
import requests
from dotenv import load_dotenv

class AppUserViewSet(ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer


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
            attributes['create_wallet'] = 'create_wallet' in roles
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
        password = request.data.get('password')

        token_response = requests.post(
            'https://keycloak.inethilocal.net/realms/Test/protocol/openid-connect/token', {
                'client_id': 'testclient',
                'client_secret': CLIENT_SECRET,
                'grant_type': 'client_credentials'
            })

        if token_response.status_code != 200:
            return Response({'error': 'Failed to authenticate with Keycloak'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token = token_response.json().get('access_token')

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        user_data = {
            'username': username,
            'enabled': True,
            'email': f'{username}@inethi.org.za',
            'firstName': f'auto_{username}',
            'lastName': f'auto_{username}',
            'credentials': [{
                'type': 'password',
                'value': password,
                'temporary': False
            }]
        }

        registration_response = requests.post(
            'http://keycloak.inethilocal.net/admin/realms/Test/users',
            json=user_data,
            headers=headers
        )

        if registration_response.status_code == 201:
            user = User.objects.create(keycloak_username=username)
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        elif registration_response.status_code == 409:
            return Response({'error': 'Username already in use.'}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({'error': 'Failed to register user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
