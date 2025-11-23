from typing import Iterable, override
from django_compose.base.components.base_components import (
    Children,
    VoidComponentMixin,
)
from django_compose.base.theme import Theme
from .components import Context
from .components.html_components import (
    Body,
    DocumentLevelComponent,
    Head,
    Html,
)
from django_compose.base.attributes import Attribute
import htpy


class Router:
    def __init__(self, *, pages: dict[str, "Page"]):
        self.pages = pages


class Page(VoidComponentMixin, DocumentLevelComponent):
    def __init__(
        self,
        name: str,
        *attributes: Attribute | Iterable[Attribute],
        children: Children = None,
        theme: Theme | None = None,
        head: Children = None,
        body: Children = None,
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

    @override
    def build(self, context: Context, children: Children) -> "DocumentLevelComponent":
        return Html()[children]

    @override
    def render(self) -> htpy.Renderable:
        theme = self.theme or Theme()
        context = Context(theme)
        root = self.full_build(context)
        return root.render()


class DjangoApp:
    def __init__(
        self,
        *,
        style: str | None = None,
        starts_on: str = "index",
        pages: Iterable[Page],
    ):
        self.style = style
        self.starts_on = starts_on
        self.pages = {page.name: page for page in pages}

    def render(self) -> htpy.Renderable:
        return self.pages[self.starts_on].render()
