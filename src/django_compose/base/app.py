from collections.abc import Iterable
from typing import TYPE_CHECKING, cast

import htpy
from typing_extensions import override

from django_compose.base.components.base_components import (
    Children,
    Component,
    ComponentLike,
    ModifierLike,
    VoidComponentMixin,
)
from django_compose.base.context import Context, ContextData, DataDict
from django_compose.base.router import Router
from django_compose.base.theme import Theme
from django_compose.base.views.view_base import ComposePageView

from .components.html_components import (
    Body,
    DocumentLevelComponent,
    Head,
    Html,
)


class Page(VoidComponentMixin, Component):
    def __init__(
        self,
        *modifiers: ModifierLike,
        name: str,
        children: Children = None,
        theme: Theme | None = None,
        head: Children = None,
        body: Children = None,
        view: type[ComposePageView] | None = None,
        route_pattern: str | None = None,
        data: list[ContextData] | None = None,
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
        self.data = data or []

    @override
    def provide(self, data: DataDict) -> None:
        for d in self.data:
            data[d.__class__] = d

    @override
    def full_build(self, context: Context) -> DocumentLevelComponent:
        if self.theme is not None:
            context = context.copy_with(theme=self.theme)
        context = context.copy_with(page=self)
        self._build_result = cast("DocumentLevelComponent", super().full_build(context))
        return self._build_result

    @override
    def build(self, context: Context, children: Children) -> Children:
        return children

    @override
    def render(self) -> htpy.Renderable:
        if self._build_result is None:
            raise ValueError("Page must be built before rendering.")
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
        # theme = self.theme or Theme()
        context = Context(router=self.router)
        for route in self.router:
            route.page.full_build(context)
