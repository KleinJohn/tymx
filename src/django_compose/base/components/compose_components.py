from typing import override

import django_compose.base.attributes as a
import django_compose.base.components.html_components as html
from django_compose.base.components.base_components import (
    Children,
    Component,
    NoChildren,
)
from django_compose.base.context import Context


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
