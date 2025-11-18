from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Iterator, Self, override

from django_compose.base.modifiers.attributes import Attribute

if TYPE_CHECKING:
    from django_compose.base.components.base_components import Component, Context


class Modifier(ABC):

    @abstractmethod
    def apply(self, context: Context, component: Component) -> Component:
        """Injects behavior into the given component after the build process.

        It is safe to modify the component in place and return the same instance.
        It is also possible to return a new instance of the component if needed.
        """
        raise NotImplementedError()


class Attributes(Modifier):
    def __init__(self, *attributes: Attribute) -> None:
        self.data: OrderedDict[str, Attribute] = OrderedDict()
        for attr in attributes:
            self.add(attr)

    def __call__(self) -> Self:
        return self

    def __iter__(self) -> Iterator[Attribute]:
        return iter(self.data.values())

    def __contains__(self, item: str | Attribute) -> bool:
        if isinstance(item, str):
            return item in self.data
        return item.name in self.data

    def __str__(self) -> str:
        return " ".join(str(attr) for attr in self.data.values())

    def values(self) -> dict[str, Any]:
        return {attr.name: attr.value for attr in self.data.values()}

    def add(self, attribute: Attribute) -> None:
        if attribute.name not in self.data:
            self.data[attribute.name] = attribute
        else:
            self.data[attribute.name].merge(attribute)

    def add_all(self, attributes: "Attributes") -> None:
        for attr in attributes:
            self.add(attr)

    @override
    def apply(self, context: Context, component: Component) -> Component:
        component.attributes.add_all(self)
        return component
