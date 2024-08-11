from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppUserViewSet
from .views import AppUserViewSet, UserKeycloakAttributes, RegisterKeycloakUser
router = DefaultRouter()
router.register(r'appUsers', AppUserViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('keycloak/attributes/', UserKeycloakAttributes.as_view(), name='keycloak-attributes'),
    path('keycloak/register/', RegisterKeycloakUser.as_view(), name='keycloak-register'),
]