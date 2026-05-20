from typing import override

from attrs import field

import tymx.base.attributes as a
import tymx.base.components.html_components as html
from tymx.base.components.base_components import (
    Children,
    Component,
    NoChildren,
    children_to_tuple,
)
from tymx.base.context import Context, ContextData, DataDict
from tymx.base.views.view_base import ComponentView


def _route_pattern_not_none(route_pattern: str | None) -> str:
    # Actually returns str | None, but is turned into str by __attrs_post_init__
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


class Stylesheet(NoChildren, Component):
    href: str

    @override
    def build(self, context: Context) -> Children:
        return html.Link((a.rel("stylesheet"), a.href(self.href)))


# class PageLink(TemplateComponent):
#     def __init__(
#         self, *modifiers: ModifiersOrAttributes, to: str, **kwargs: Any
#     ) -> None:
#         super().__init__(*modifiers, **kwargs)
#         self.use_props(to=to)
#         self.to = to

#     @override
#     def build(self, context: Context, children: Children) -> Children:
#         return A(href(context.router.get_url(self.to)))[children]
