from importlib import import_module

from django.core.exceptions import ImproperlyConfigured

from django.urls.resolvers import LocalePrefixPattern, URLResolver
from typing import cast

from tymx.django import App


def include_tymx(
    app: App, namespace=None
) -> tuple[list[URLResolver], str | None, str | None]:
    app.build()
    patterns = app.router.get_urlpatterns()
    app_name = app.name
    namespace = namespace or app_name
    return (cast(list[URLResolver], patterns), app_name, namespace)
