from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_compose.base.app import Router
    from django_compose.base.theme import Theme


class Context:
    """Context for building and rendering components.

    The context can hold information that is relevant during the build and render process.
    """

    def __init__(self, theme: Theme, router: Router) -> None:
        self.theme = theme
        self.router = router

    def copy_with(self, **kwargs) -> "Context":
        theme = kwargs.get("theme", self.theme)
        router = kwargs.get("router", self.router)
        return Context(theme=theme, router=router)
