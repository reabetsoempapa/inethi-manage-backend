from rest_framework.viewsets import ModelViewSet
from .models import AppUser
from .serializers import AppUserSerializer

class AppUserViewSet(ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer


