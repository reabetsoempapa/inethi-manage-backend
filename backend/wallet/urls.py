from rest_framework import routers
from .views import WalletViewSet


router = routers.SimpleRouter()
router.register("", WalletViewSet, basename="wallet")

urlpatterns = router.urls
