from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Any

from django_compose.base.context import ConsumerPolicy

from .base_modifiers import Modifier

if TYPE_CHECKING:
    from django_compose.base.components.base_components import Component
    from django_compose.base.context import Context


class DebugModifier(Modifier):
    def apply_before_build(self, context: Context, component: Component) -> None:
        print(f"Before building: {component}")

    def apply_to_child(self, context: Context, component: Component) -> Component:
        print(f"After building: {component}")
        return component


class PrintContextModifier(Modifier):
    consumer_policy = ConsumerPolicy.ALL_CHILDREN

    def apply_before_build(self, context: Context, component: Component) -> None:
        super().apply_before_build(context, component)
        print(
            f"{component.__class__.__name__:<20}\t",
            str(context),
        )


class PrintComponentModifier(Modifier):
    consumer_policy = ConsumerPolicy.NONE

    def __init__(self, pretty: bool = True, verbose: bool = True, **print_kwargs: Any) -> None:
        super().__init__()
        self.pretty = pretty
        self.verbose = verbose
        self.print_kwargs = print_kwargs

    def apply_to_child(self, context: Context, component: Component) -> Component:
        print(component.__str__(self.pretty, self.verbose, **self.print_kwargs))
        return super().apply_to_child(context, component)
