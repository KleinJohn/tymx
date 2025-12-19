from __future__ import annotations
from typing import TYPE_CHECKING, Any, Iterable, Iterator

from django.urls import URLPattern, path, reverse

from django_compose.base.modifiers.compose_modifiers import NavigationModifier

if TYPE_CHECKING:
    from django_compose.base.app import Page


class Route:
    def __init__(self, page: Page):
        self.page = page

    @property
    def url(self) -> str:
        return reverse(self.page.name)


class Router:
    def __init__(self, *, pages: Iterable[Page], **view_kwargs: Any):
        self.routes = {page.name: Route(page) for page in pages}
        self._view_kwargs = view_kwargs
        self._iter = iter(self.routes.values())

    def __iter__(self) -> Iterator[Route]:
        self._iter = iter(self.routes.values())
        return self._iter

    def __next__(self) -> Route:
        return next(self._iter)

    def navigate(self, page_name: str) -> NavigationModifier:
        route = self.routes.get(page_name)
        if route is None:
            raise ValueError(f"Route '{page_name}' not found in router.")
        return NavigationModifier(self.routes[page_name])

    def get_urlpatterns(self) -> list[URLPattern]:
        urlpatterns: list[URLPattern] = []
        for route in self.routes.values():
            urlpatterns.append(
                path(
                    route.page.name + "/",
                    route.page.view.as_view(**self._view_kwargs),
                    name=route.page.name,
                )
            )
        return urlpatterns
