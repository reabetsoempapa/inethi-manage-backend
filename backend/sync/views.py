from revproxy.views import ProxyView


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
        response = super().dispatch(request, path)
        if self.hook_request:
            self.hook_request(request, path, response, request_data)
        return response
