from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("devices", views.NodeViewSet)
router.register("services", views.ServiceViewSet)
router.register("alerts", views.AlertsViewSet)
router.register("meshes", views.MeshViewSet)
router.register("unknown_nodes", views.UnknownNodeViewSet)

urlpatterns = [path("", include(router.urls)), path("overview/", views.overview)]
