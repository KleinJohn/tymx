import htpy
from typing_extensions import override

from django_compose.base.components.base_components import (
    BaseComponent,
    Component,
    ComponentLike,
)
from django_compose.base.context import Context


class Template(Component):
    """Templates relay the call of their build methods to the rendertime."""

    @override
    def full_build(self, context: Context) -> ComponentLike:
        """The component should return to its original state after building."""
        print("Building Template")
        self._prepare_build(context)
        self.consume()
        self._before_build()
        return self

    @override
    def _handle_build(self) -> list[BaseComponent]:
        children = self._children
        if not self.is_built:
            self._building = True
            children = self._children_to_list(self.build(self.context, self._children))
            self._building = False

        self._before_build_children(children)
        children = self._build_children(children)
        self._after_build_children(children)

        if self.is_built:
            self._children = children
            children = [self]
        return children

    @override
    def render(self) -> htpy.Node:
        print("Rendering Template")
        children = self._handle_build()
        self._after_build(children)
        return [child.render() for child in children]
