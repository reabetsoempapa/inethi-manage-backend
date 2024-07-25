from typing import Callable, Type
from datetime import datetime
import requests

from django.db import models
from django.utils.timezone import make_aware
from django.http import HttpRequest, HttpResponse
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
    api_view,
)
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


def forward_request(
    url: str,
    request: HttpRequest,
    hook_request: Callable | None = None,
    hook_response: Callable | None = None,
) -> Response:
    """Duplicate a GET or POST request to another URL."""
    if hook_request:
        hook_request(request.data)
    if request.method == "GET":
        r = requests.get(url, params=request.query_params)
    elif request.method == "POST":
        r = requests.post(url, data=request.data, params=request.query_params)
    else:
        raise ValueError(f"Unsupported method '{request.method}'")
    response_data = r.json()
    if hook_response:
        hook_response(response_data)
    return Response(response_data, status=r.status_code)


def forward_view(
    url: str,
    hook_request: Callable | None = None,
    hook_response: Callable | None = None,
) -> Callable[[HttpRequest], HttpResponse]:
    """Generate a view that forwards GET or POST requests."""

    @api_view(["GET", "POST"])
    @authentication_classes([])
    @permission_classes([])
    def view(request):
        return forward_request(url, request, hook_request, hook_response)

    return view
