from typing import Any, Callable, Iterable, TypeAlias, override

from django.urls import reverse, path
from django.urls.resolvers import URLPattern
from django_compose.base.components.base_components import (
    Children,
    VoidComponentMixin,
)
from django_compose.base.modifiers.base_modifiers import Modifier
from django_compose.base.modifiers.compose_modifiers import NavigationModifier
from django_compose.base.theme import Theme
from django_compose.base.context import Context
from .components.html_components import (
    Body,
    DocumentLevelComponent,
    Head,
    Html,
)
from django_compose.base.attributes import Attribute
import htpy


ViewType: TypeAlias = Callable[..., Response]


class Route:
    def __init__(self, name: str, view: ViewType):
        self.name = name
        self.view = view
        self.built_page: htpy.Renderable | None = None

    @property
    def url(self) -> str:
        return reverse(self.name)


class Router:
    def __init__(self, *, pages: Iterable["Page"]):
        self.routes = {page.name: Route(page.name, page.view) for page in pages}
        self._pages = {page.name: page for page in pages}

    def build(self, context: Context) -> None:
        for name, page in self._pages.items():
            self.routes[name].built_page = page.full_build(context).render()
        # TODO: ensure dynamically added routes are built

    def navigate(self, page_name: str) -> NavigationModifier:
        route = self.routes.get(page_name)
        if route is None:
            raise ValueError(f"Route '{page_name}' not found in router.")
        return NavigationModifier(self.routes[page_name])

    def get_urlpatterns(self) -> list[URLPattern]:
        urlpatterns: list[URLPattern] = []
        for route in self.routes.values():
            urlpatterns.append(path(route.name + "/", route.view, name=route.name))
        return urlpatterns


class Page(VoidComponentMixin, DocumentLevelComponent):
    def __init__(
        self,
        name: str,
        *attributes: Attribute | Iterable[Attribute],
        children: Children = None,
        theme: Theme | None = None,
        head: Children = None,
        body: Children = None,
        view: ViewType = default_view,
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
        self.view = view

    @override
    def build(self, context: Context, children: Children) -> "DocumentLevelComponent":
        return Html()[children]

    @override
    def render(self, context: Context | None = None) -> htpy.Renderable:
        if context is None:
            raise ValueError("Context must be provided to render the page.")
        if self.theme is not None:
            context = context.copy_with(theme=self.theme)
        root = self.full_build(context)
        return root.render()


class ComposeApp:
    def __init__(
        self,
        *,
        starts_on: str,
        pages: Iterable[Page],
        style: str | None = None,
        theme: Theme | None = None,
    ):
        self.style = style
        self.theme = theme
        self.starts_on = starts_on
        self.router = Router(
            pages={page.name: page for page in pages},
        )

    def build(self) -> None:
        theme = self.theme or Theme()
        context = Context(theme=theme, router=self.router)
        return self.router.build(context)
