from django.http import HttpResponse
from django.shortcuts import render
from django.urls import URLPattern, path
import htpy
from django_compose.base.page import ComposeApp, Route


def _response_to_http(route: Route) -> HttpResponse:
    return HttpResponse(route.content)


def to_urlpatterns(app: ComposeApp) -> list[URLPattern]:
    """Convert a ComposeApp to Django URL patterns."""
    return [path() for page in app.router.routes]
