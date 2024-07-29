import logging

from revproxy.views import ProxyView
from django.http import HttpResponse
from urllib3.exceptions import MaxRetryError

logger = logging.getLogger(__file__)


class HookProxyView(ProxyView):
    """Proxy view that can call a hook before and after the proxy call."""

    hook_request = None

    def __init__(self, *args, hook_request=None, **kwargs):
        self.hook_request = hook_request
        super().__init__(*args, **kwargs)

    def dispatch(self, request, path: str):
        """Call hook_request before and after dispatch."""
        request_data = None
        if self.hook_request:
            request_data = self.hook_request(request, path)
        try:
            response = super().dispatch(request, path)
        except MaxRetryError:
            # 504 gateway timeout
            logger.error("Error forwarding request to %s, max retries reached", self.upstream)
            return HttpResponse(status=504)
        if self.hook_request:
            self.hook_request(request, path, response, request_data)
        return response
