from typing import Iterable, override
from django_compose.base.components.base_components import (
    ComponentBaseChildren,
)
from django_compose.base.theme import Theme
from .components import Context
from .components.html_components import (
    Body,
    DocumentLevelComponent,
    Head,
    Html,
    ComponentChildren,
)
from django_compose.base.modifiers.attributes import Attribute
import htpy


class Router:
    def __init__(self, *, pages: dict[str, "Page"]):
        self.pages = pages


class Page(DocumentLevelComponent):
    def __init__(
        self,
        name: str,
        *attributes: Attribute | Iterable[Attribute],
        children: ComponentBaseChildren = None,
        theme: Theme | None = None,
        head: ComponentChildren = None,
        body: ComponentChildren = None,
        **htpy_kwargs: str,
    ):
        super().__init__(
            *attributes,
            children=children,
            **htpy_kwargs,
        )
        self.name = name
        self.head = head
        self.body = body
        self.theme = theme

    @override
    def build(
        self, context: Context, children: ComponentBaseChildren
    ) -> DocumentLevelComponent:
        return Html[Head[self.head], Body[self.body]]

    @override
    def full_build(self, context: Context) -> DocumentLevelComponent:
        self_built = self.build(context, self.children)
        if self.__class__.inherit_attributes:
            self_built.attributes.add_all(self.attributes)
        return self_built

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
