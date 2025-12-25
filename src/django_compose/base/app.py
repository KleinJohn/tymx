from typing import Iterable, override

from django_compose.base.components.base_components import (
    Children,
    ComponentLike,
    ModifierLike,
    VoidComponentMixin,
    Component,
)
from django_compose.base.modifiers.base_modifiers import PageRenderModifier
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


class Page(VoidComponentMixin, Component):

    def __init__(
        self,
        name: str,
        *modifiers: ModifierLike,
        children: Children = None,
        theme: Theme | None = None,
        head: Children = None,
        body: Children = None,
        view: type[ComposePageView] | None = None,
        route_pattern: str | None = None,
        htpy_kwargs: dict[str, str] | None = None,
    ):
        super().__init__(
            *modifiers,
            children=Html[Head[head], Body[body]],
            htpy_kwargs=htpy_kwargs,
        )
        self.name = name
        self.head = head
        self.body = body
        self.theme = theme
        self._build_result: DocumentLevelComponent | None = None
        self.view = view or ComposePageView
        self.route_pattern = f"{self.name}/" if route_pattern is None else route_pattern
        self.render_time_modifiers: list[PageRenderModifier] = []

    @override
    def full_build(self, context: Context) -> ComponentLike:
        if self.theme is not None:
            context = context.copy_with(theme=self.theme)
        context = context.copy_with(page=self)
        return super().full_build(context)

    @override
    def build(self, context: Context, children: Children) -> Children:
        return children

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
        self.router = Router(self.name, pages=pages)

    def build(self) -> None:
        theme = self.theme or Theme()
        context = Context(router=self.router)
        for route in self.router:
            route.page.full_build(context)
