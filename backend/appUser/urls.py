from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppUserViewSet

router = DefaultRouter()
router.register(r'appUsers', AppUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
]