from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_compose.base.app import Router, Page
    from django_compose.base.theme import Theme


class Context:
    """Context for building and rendering components."""

    def __init__(self, theme: Theme, router: Router, page: Page | None = None) -> None:
        self.theme = theme
        self.router = router
        self.page = page

    def copy(self) -> "Context":
        return self.copy_with()

    def copy_with(self, **kwargs) -> "Context":
        theme = kwargs.get("theme", self.theme)
        router = kwargs.get("router", self.router)
        page = kwargs.get("page", self.page)
        return Context(theme=theme, router=router, page=page)

    @property
    def url(self) -> str:
        if not self.page:
            raise ValueError("No page found in context.")
        return self.router.routes[self.page.name].url
