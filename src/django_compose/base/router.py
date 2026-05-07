from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import URLPattern, path, reverse_lazy
from typing_extensions import Any

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from django_compose.base.app import Page, DjangoApp


class Route:
    def __init__(self, app_name: str, page: Page):
        self.app_name = app_name
        self.page = page

    @property
    def url(self) -> str:
        """Only call this when Django is fully loaded (render time)"""
        return str(reverse_lazy(f"{self.app_name}:{self.page.name}"))


class Router:
    def __init__(self, app: DjangoApp, *, pages: Iterable[Page], **view_kwargs: Any):
        self.app = app
        self.routes: dict[str, Route] = {
            page.name: Route(self.app.name, page) for page in pages
        }
        self._view_kwargs = view_kwargs
        self._iter = iter(self.routes.values())

    def __iter__(self) -> Iterator[Route]:
        self._iter = iter(self.routes.values())
        return self._iter

    def __next__(self) -> Route:
        return next(self._iter)

    def get_url(self, page_name: str) -> str:
        route = self.routes.get(page_name)
        if route is None:
            raise ValueError(f"Route '{page_name}' not found in router.")
        return route.url

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
