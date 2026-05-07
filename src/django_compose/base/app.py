from __future__ import annotations

from collections.abc import Iterable
from typing import override

from attrs import field

from django_compose.base.components import Component, NoChildren

from django_compose.base.components.base_components import children_to_tuple
from django_compose.base.theme import Theme
from django_compose.base.types import Children

from django_compose.base.context import Context, ContextData, DataDict
from django_compose.base.router import Router

import django_compose.base.components.html_components as html
from django_compose.base.views.view_base import ComponentView


def _route_pattern_not_none(route_pattern: str | None) -> str:
    # route_pattern is set base on name in __attrs_post_init__ if None
    return route_pattern  # type: ignore[return-value]


class Page(Component):

    name: str
    head: tuple[Component, ...] = field(converter=children_to_tuple, default=None)
    view: type[ComponentView] = ComponentView
    route_pattern: str = field(converter=_route_pattern_not_none, default=None)
    context_data: tuple[ContextData, ...] = field(factory=tuple)

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if self.route_pattern is None:
            object.__setattr__(
                self,
                "route_pattern",
                f"{self.name}/" if self.route_pattern is None else self.route_pattern,
            )

    @override
    def build(self, context: Context) -> Children:
        return html.Html[
            html.Head[self.head],
            html.Body[self.children],
        ]

    @override
    def provide(self, data: DataDict) -> None:
        super().provide(data)
        for d in self.context_data:
            data.add(d)


class DjangoApp:
    def __init__(
        self,
        *,
        name: str,
        pages: Iterable[Page],
    ):
        self.name = name
        self.router = Router(self, pages=pages)
        # App-level cache for built (document-level) page results. Keyed by page name.
        self.built_pages: dict[str, Component] = {}

    def build(self) -> None:
        context = Context(router=self.router)
        for route in self.router:
            built = route.page.full_build(context)
            # can access [0] since page returns single html component
            self.built_pages[route.page.name] = built[0]
