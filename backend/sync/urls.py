from django.conf import settings
from django.urls import re_path

from .radiusdesk.hooks import hook_rd
from .unifi.hooks import hook_unifi
from .views import HookProxyView

urlpatterns = []

if settings.RD_URL:
    urlpatterns.append(
        re_path(
            r"rd/(?P<path>.*)",
            HookProxyView.as_view(
                upstream=settings.RD_URL,
                hook_request=hook_rd,
            ),
        ),
    )

if settings.UNIFI_URL:
    urlpatterns.append(
        re_path(
            r"unifi/(?P<path>.*)",
            HookProxyView.as_view(
                upstream=settings.UNIFI_URL,
                hook_request=hook_unifi,
            ),
        ),
    )
