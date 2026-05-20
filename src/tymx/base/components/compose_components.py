from typing import override

from attrs import field

import tymx.base.attributes as a
import tymx.base.components.html_components as html
from tymx.base.components.base_components import (
    Children,
    Component,
    NoChildren,
    TemplateComponent,
    children_to_tuple,
)
from tymx.base.context import Context, ContextData, DataDict


class Page(Component):
    head: tuple[Component, ...] = field(converter=children_to_tuple, default=None)
    context_data: tuple[ContextData, ...] = field(factory=tuple)

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


class PageLink(TemplateComponent):
    to: str

    @override
    def build(self, context: Context) -> Children:
        return html.A(a.href(context.router.get_page_url(self.to)))[self.children]
