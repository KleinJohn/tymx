from compose.base.component_base import (
    Component,
    Context,
    Body,
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
        self.head = Head[head]
        self.body = Body[body]

    def render(self) -> htpy.Renderable:
        context = Context()
        doc = Html[self.head, self.body]
        print(doc)
        return doc.build(context).render(context)


class DjangoApp:
    def __init__(self, *, style: str | None = None, starts_on: Page):
        self.style = style
        self.starts_on = starts_on
