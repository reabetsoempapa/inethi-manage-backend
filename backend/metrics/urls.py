from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("uptime", views.UptimeViewSet)
router.register("rtt", views.RTTViewSet)
router.register("resources", views.ResourcesViewSet)
router.register("data_usage", views.DataUsageViewSet)
router.register("data_rate", views.DataRateViewSet)
router.register("failures", views.FailuresViewSet)

urlpatterns = [path("", include(router.urls))]
