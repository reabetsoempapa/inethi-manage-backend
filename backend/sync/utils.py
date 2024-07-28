from typing import Callable, Type
from datetime import datetime
import requests

from django.db import models
from django.utils.timezone import make_aware
from django.http import HttpRequest, HttpResponse
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
    parser_classes,
    api_view,
)
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
import pytz


def bulk_sync(ModelType: Type[models.Model], delete: bool = False):
    """Log output for sync, with number of added, updated and deleted models."""

    def outer(syncfunc):
        def inner(cursor):
            ids_to_delete = set(ModelType.objects.values_list("pk", flat=True))
            n_added, n_updated = 0, 0
            for result in syncfunc(cursor):
                create_defaults = None
                if len(result) == 2:
                    update_defaults, kwargs = result
                else:
                    update_defaults, create_defaults, kwargs = result
                model, created = ModelType.objects.update_or_create(
                    defaults=update_defaults, create_defaults=create_defaults, **kwargs
                )
                if created:
                    n_added += 1
                else:
                    n_updated += 1
                ids_to_delete.discard(model.pk)
            n_deleted = 0
            if delete:
                n_deleted, _ = ModelType.objects.filter(pk__in=ids_to_delete).delete()
            print(
                f"Updated {ModelType.__name__:>12} models "
                f"({n_added} created, {n_updated} updated, {n_deleted} deleted)"
            )

        return inner

    return outer


def aware_timestamp(v: int) -> datetime:
    """Generate an aware datetime from epoch timestamp."""
    return make_aware(datetime.fromtimestamp(v / 1e3), pytz.UTC)


def get_src_ip(request: HttpRequest) -> str:
    """Get source IP address."""
    # From https://stackoverflow.com/q/4581789/7337283
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def forward_request(
    url: str,
    request: HttpRequest,
    hook_request: Callable | None,
    hook_response: Callable | None,
) -> Response:
    """Duplicate a GET or POST request to another URL."""
    if hook_request:
        hook_request(request.data, request)
    # TODO: Need to set HTTP_X_FORWARDED_FOR so that the destination get the correct source IP
    r = requests.request(
        request.method,
        url,
        params=request.query_params,
        data=request.data,
        headers=request.headers,
        cookies=request.COOKIES,
        timeout=20
    )
    try:
        response_data = r.json()
    except requests.exceptions.JSONDecodeError:
        response_data = r.content
    if hook_response:
        data = hook_response(response_data, request)
        return Response(data, status=r.status_code)
    return HttpResponse(r.content, status=r.status_code)


def forward_view(
    url: str,
    hook_request: Callable | None = None,
    hook_response: Callable | None = None,
    parser=JSONParser,
) -> Callable[[HttpRequest], HttpResponse]:
    """Generate a view that forwards GET or POST requests."""

    @api_view(["GET", "POST"])
    @parser_classes([parser])
    @authentication_classes([])
    @permission_classes([])
    def view(request):
        return forward_request(url, request, hook_request, hook_response)

    return view
