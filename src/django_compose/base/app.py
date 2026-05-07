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


class Page(NoChildren, Component):

    name: str
    head: tuple[Component, ...] = field(converter=children_to_tuple)
    body: tuple[Component, ...] = field(converter=children_to_tuple)
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
            html.Body[self.body],
        ]

    @override
    def provide(self, data: DataDict) -> None:
        super().provide(data)
        for d in self.context_data:
            data.add(d)


# class Page(NoChildren, Component):
# def __init__(
#     self,
#     *modifiers: ModifiersOrAttributes,
#     name: str,
#     head: Children,
#     body: Children,
#     children: Children = None,
#     theme: Theme | None = config.default_theme,
#     view: type[ComposePageView] | None = None,
#     route_pattern: str | None = None,
#     data: list[ContextData] | None = None,
#     htpy_kwargs: dict[str, str] | None = None,
# ):
#     super().__init__(
#         *modifiers,
#         children=children,
#         theme=theme,
#         htpy_kwargs=htpy_kwargs,
#     )
#     self.use_props(
#         name=name,
#         head=head,
#         body=body,
#         view=view,
#         route_pattern=route_pattern,
#         data=data,
#     )
#     self.name = name
#     self.head = head
#     self.body = body
#     self._build_result: DocumentLevelComponent | None = None
#     self.view = view or ComposePageView
#     self.route_pattern = f"{self.name}/" if route_pattern is None else route_pattern
#     self.data = data or []
#     if self._theme is None:
#         self._theme = default_theme

# @override
# def provide(self, data: DataDict) -> None:
#     for d in self.data:
#         data[d.__class__] = d
#     data.add(self.theme)

# @override
# def full_build(self, context: Context) -> DocumentLevelComponent:
#     context = context.copy_with(page=self)
#     self._build_result = cast("DocumentLevelComponent", super().full_build(context))
#     return self._build_result

# @override
# def build(self, context: Context) -> Children:
#     return Html[
#         Head,
#         Body,
#     ]

# @override
# def render(self) -> htpy.Renderable:
#     if self._build_result is None:
#         raise ValueError("Page must be built before rendering.")
#     return self._build_result.render()


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
