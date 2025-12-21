from typing import Iterable, override

from django_compose.base.components.base_components import (
    Children,
    VoidComponentMixin,
)
from django_compose.base.modifiers.base_modifiers import DeferredModifier
from django_compose.base.router import Router
from django_compose.base.theme import Theme
from django_compose.base.context import Context
from django_compose.base.views.view_base import ComposePageView
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
        view: type[ComposePageView] | None = None,
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
        self._build_result: DocumentLevelComponent | None = None
        self.view = view or ComposePageView
        self.render_time_modifiers: list[DeferredModifier] = []

    @override
    def build(self, context: Context, children: Children) -> "DocumentLevelComponent":
        return Html()[children]

    @override
    def full_build(self, context: Context | None = None) -> "DocumentLevelComponent":
        if context is None:
            raise ValueError("Context must be provided to render the page.")
        if self.theme is not None:
            context = context.copy_with(theme=self.theme)
        context = context.copy_with(page=self)
        self._build_result = super().full_build(context)
        return self._build_result

    @override
    def render(self) -> htpy.Renderable:
        if self._build_result is None:
            raise ValueError("Page must be built before rendering.")
        for modifier in self.render_time_modifiers:
            modifier.notify()
        return self._build_result.render()


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
            route.page.full_build(context)
