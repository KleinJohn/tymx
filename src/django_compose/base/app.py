from typing import Iterable, override

from django_compose.base.components.base_components import (
    Children,
    VoidComponentMixin,
)
from django_compose.base.router import Router
from django_compose.base.theme import Theme
from django_compose.base.context import Context
from django_compose.base.views.view_base import ComposeView
from .components.html_components import (
    Body,
    DocumentLevelComponent,
    Head,
    Html,
)
from django_compose.base.attributes import Attribute
import htpy


class Page(VoidComponentMixin, DocumentLevelComponent):
    def __init__(
        self,
        name: str,
        *attributes: Attribute | Iterable[Attribute],
        children: Children = None,
        theme: Theme | None = None,
        head: Children = None,
        body: Children = None,
        view: type[ComposeView] | None = None,
        **htpy_kwargs: str,
    ):
        super().__init__(
            *attributes,
            children=(Head[head], Body[body]),
            **htpy_kwargs,
        )
        self.name = name
        self.head = head
        self.body = body
        self.theme = theme
        self.content: htpy.Renderable | None = None
        self.view = view or ComposeView

    @override
    def build(self, context: Context, children: Children) -> "DocumentLevelComponent":
        return Html()[children]

    @override
    def render(self, context: Context | None = None) -> htpy.Renderable:
        if context is None:
            raise ValueError("Context must be provided to render the page.")
        if self.theme is not None:
            context = context.copy_with(theme=self.theme)
        self.content = self.full_build(context).render()
        return self.content


class ComposeApp:
    def __init__(
        self,
        *,
        name: str,
        starts_on: str,
        pages: Iterable[Page],
        style: str | None = None,
        theme: Theme | None = None,
    ):
        self.name = name
        self.style = style
        self.theme = theme
        self.starts_on = starts_on
        self.router = Router(pages=pages)

    def build(self) -> None:
        theme = self.theme or Theme()
        context = Context(theme=theme, router=self.router)
        for route in self.router:
            built_page = route.page.render(context)
            route.page.content
