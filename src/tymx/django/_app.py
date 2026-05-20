from __future__ import annotations
from importlib.util import find_spec
from typing import Any, override

from attrs import field
from django.views import View

from tymx.django._views import ComponentView

if find_spec("django") is None:
    raise ImportError(
        "tymx.django requires the optional 'django' dependency. "
        "Install tymx[django] to use these integrations."
    )

from django.urls import URLPattern, path, reverse_lazy


from tymx.base.app import AbstractRouter, AbstractRoute, AbstractApp


class Route(AbstractRoute, frozen=True):
    route_pattern: str | None = None
    view: type[View] = ComponentView
    view_kwargs: dict[str, Any] = field(factory=dict)


class Router(AbstractRouter[Route]):

    @override
    def get_urlpatterns(self) -> list[URLPattern]:
        urlpatterns: list[URLPattern] = []
        for name, route in self.routes.items():
            component = self.app.built_pages.get(name)
            urlpatterns.append(
                path(
                    f"{name}/" if route.route_pattern is None else route.route_pattern,
                    route.view.as_view(component=component, **route.view_kwargs),
                    name=name,
                )
            )
        return urlpatterns

    @override
    def get_url(self, route: Route) -> str:
        name = next((k for k, r in self.routes.items() if r is route), None)
        if name is None:
            raise ValueError(f"Route not found in router.")
        return str(reverse_lazy(f"{self.app.name}:{name}"))


class App(AbstractApp[Router]):
    pass
