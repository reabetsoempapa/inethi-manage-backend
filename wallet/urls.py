from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreateWallet, SendToken, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('create/', CreateWallet.as_view()),
    path('send_token/', SendToken.as_view()),
]