from __future__ import annotations
from importlib.util import find_spec
from typing import override

if find_spec("django") is None:
    raise ImportError(
        "tymx.django requires the optional 'django' dependency. "
        "Install tymx[django] to use these integrations."
    )

from django.urls import URLPattern, path, reverse_lazy


from tymx.base.app import AbstractRouter, AbstractRoute, AbstractApp


class Route(AbstractRoute):

    @property
    @override
    def url(self) -> str:
        return str(reverse_lazy(f"{self.app_name}:{self.page.name}"))


class Router(AbstractRouter[Route]):

    @override
    def get_urlpatterns(self) -> list[URLPattern]:
        urlpatterns: list[URLPattern] = []
        for route in self.routes.values():
            component = self.app.built_pages.get(route.page.name)
            urlpatterns.append(
                path(
                    route.page.route_pattern,
                    route.page.view.as_view(component=component, **self._view_kwargs),
                    name=route.page.name,
                )
            )
        return urlpatterns


class App(AbstractApp[Router]):
    pass
