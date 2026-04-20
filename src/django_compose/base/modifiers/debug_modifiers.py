from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Any

from django_compose.base.context import ConsumerPolicy

from .base_modifiers import Modifier

if TYPE_CHECKING:
    from django_compose.base.components.base_components import Component
    from django_compose.base.context import Context


class DebugModifier(Modifier):
    def apply(self, context: Context, component: Component) -> None:
        print(f"Before building: {component}")

    def transform(self, context: Context, component: Component) -> Component:
        print(f"After building: {component}")
        return component


class PrintContextModifier(Modifier):
    consumer_policy = ConsumerPolicy.ALL_CHILDREN

    def apply(self, context: Context, component: Component) -> None:
        super().apply(context, component)
        print(
            f"{component.__class__.__name__:<20}\t",
            str(context),
        )


class PrintComponentsModifier(Modifier):
    """Prints the component and all its children with additional options for formatting."""

    consumer_policy = ConsumerPolicy.NONE

    def __init__(
        self, pretty: bool = True, verbose: bool = True, **print_kwargs: Any
    ) -> None:
        super().__init__()
        self.pretty = pretty
        self.verbose = verbose
        self.print_kwargs = print_kwargs

    def transform(self, context: Context, component: Component) -> Component:
        print(component.to_string(self.pretty, self.verbose, **self.print_kwargs))
        return super().transform(context, component)


class PrintComponentModifier(Modifier):
    """Prints the applied component itself."""

    consumer_policy = ConsumerPolicy.NONE

    def __init__(self, verbose: bool = False) -> None:
        super().__init__()
        self.verbose = verbose

    def apply(self, context: Context, component: Component) -> None:
        if self.verbose:
            print(f"Applying to component: {component}")
        else:
            print(component)

    def transform(self, context: Context, component: Component) -> Component:
        if self.verbose:
            print(f"{self.consumer_policy}: {component}")
        else:
            print(component)
        return super().transform(context, component)


class PrintAllChildrenModifier(PrintComponentModifier):
    consumer_policy = ConsumerPolicy.ALL_CHILDREN


class PrintDirectChildrenModifier(PrintComponentModifier):
    consumer_policy = ConsumerPolicy.DIRECT_CHILDREN


class PrintDirectBuiltChildrenModifier(PrintComponentModifier):
    consumer_policy = ConsumerPolicy.DIRECT_BUILT_CHILDREN


class PrintAllBuiltChildrenModifier(PrintComponentModifier):
    consumer_policy = ConsumerPolicy.ALL_BUILT_CHILDREN
