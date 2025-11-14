from django_compose.base.components import (
    Component,
    Context,
    Body,
    DocumentLevelComponent,
    Head,
    Html,
)
import htpy


class Router:
    def __init__(self, *, pages: dict[str, "Page"]):
        self.pages = pages


class Page:
    def __init__(
        self, *, name: str, head: Component | None = None, body: Component | None = None
    ):
        self.name = name
        self.head = head
        self.body = body

    def build(self, context: Context) -> DocumentLevelComponent:
        return Html[Head[self.head], Body[self.body]]

    def render(self) -> htpy.Renderable:
        context = Context()
        return self.build(context).render(context)


class DjangoApp:
    def __init__(self, *, style: str | None = None, starts_on: Page):
        self.style = style
        self.starts_on = starts_on
