from __future__ import annotations
from typing import TYPE_CHECKING
from django_compose.base.components.base_components import Component, Context
from django_compose.base.context import Context
from django_compose.base.modifiers.base_modifiers import DeferredModifier, Modifier
from django_compose.base.attributes import href

if TYPE_CHECKING:
    from django_compose.base.router import Route


class NavigationModifier(DeferredModifier):

    def apply(self, context: Context, component: Component) -> None:
        super().apply(context, component)
        if not context.page:
            raise ValueError("No page found in context.")
        context.page.render_time_modifiers.append(self)

    def deferred_apply(self, context: Context, component: Component) -> None:
        super().deferred_apply(context, component)
        print("deferred apply:", type(component), "url: ", context.url)
        component.attributes.add(href(context.url))


class DebugModifier(Modifier):
    def apply(self, context: Context, component: Component) -> None:
        print(f"Before building {component.__class__.__name__}: {component}")

    def apply_after_build(self, context: Context, component: Component) -> None:
        print(f"After building {component.__class__.__name__}: {component}")
