from django.conf import settings
from django.urls import path

from .radiusdesk.hooks import hook_reports
from .utils import forward_view

urlpatterns = [
    path(
        "rd/submit_report/",
        forward_view(settings.RD_REPORT_URL, hook_request=hook_reports),
    ),
    path("rd/get_actions/", forward_view(settings.RD_ACTIONS_URL)),
    path("rd/get_config/", forward_view(settings.RD_CONFIG_URL)),
]
