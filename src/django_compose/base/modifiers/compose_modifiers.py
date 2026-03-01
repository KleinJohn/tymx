from __future__ import annotations

from typing import TYPE_CHECKING

from django_compose.base.attributes import href
from django_compose.base.modifiers import PageRenderModifier

if TYPE_CHECKING:
    from django_compose.base.components.base_components import Component
    from django_compose.base.context import Context
    from django_compose.base.router import Route


class NavigationModifier(PageRenderModifier):
    """Make sure to instantiate a new NavigationModifier for each use."""

    def __init__(self, route: Route) -> None:
        super().__init__()
        self._route = route

    def apply_when_notified(self, context: Context, component: Component) -> None:
        component.attributes.add(href(self._route.url))
