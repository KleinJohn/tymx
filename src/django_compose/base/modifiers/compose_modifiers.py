from __future__ import annotations
from typing import TYPE_CHECKING

from django_compose.base.context import ConsumerPolicy
from .base_modifiers import PageRenderModifier, Modifier
from django_compose.base.attributes import href

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


class DebugModifier(Modifier):
    def apply_before_build(self, context: Context, component: Component) -> None:
        print(f"Before building: {component}")

    def apply(self, context: Context, component: Component) -> Component:
        print(f"After building: {component}")
        return component


class PrintContextModifier(Modifier):
    consumer_policy = ConsumerPolicy.ALL_CHILDREN

    def apply_before_build(self, context: Context, component: Component) -> None:
        super().apply_before_build(context, component)
        print(
            f"{component.__class__.__name__:<20}\t",
            [
                list(map(lambda f: f.__name__, s.data.keys()))
                for s in context._data_stack
            ],
        )
