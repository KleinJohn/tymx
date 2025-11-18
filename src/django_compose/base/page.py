from typing import Iterable, override
from django_compose.base.components.base_components import (
    ComponentBase,
    ComponentBaseChildren,
    ComponentChildren,
    GenericComponentLike,
    VoidComponentMixin,
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


class Page(VoidComponentMixin, DocumentLevelComponent):
    def __init__(
        self,
        name: str,
        *attributes: Attribute | Iterable[Attribute],
        children: ComponentChildren = None,
        theme: Theme | None = None,
        head: ComponentChildren = None,
        body: ComponentChildren = None,
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
    def build(
        self, context: Context, children: ComponentBaseChildren
    ) -> GenericComponentLike["DocumentLevelComponent"]:
        return Html[children]

    @override
    def full_build(self, context: Context) -> tuple[ComponentBase, ...]:
        children = (child.full_build(context) for child in self.children)
        built_self = self.build(context, children)
        components = Page._fill_component_base_children(built_self)
        if self.__class__.inherit_attributes:
            for component in components:
                component.attributes.add_all(self.attributes)
        return tuple(components)

    @override
    def render(self) -> htpy.Renderable:
        theme = self.theme or Theme()
        context = Context(theme)
        root = self.full_build(context)
        if not len(root) == 1 or not isinstance(root[0], Html):
            raise ValueError("Page must build to a single Html component.")
        return root[0].render()


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
