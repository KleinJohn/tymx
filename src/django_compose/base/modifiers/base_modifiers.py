from __future__ import annotations
from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Sequence,
    Any,
    Iterator,
    Self,
    TypeVar,
    final,
    override,
)
from collections import OrderedDict

from django_compose.base.context import Consumable, ConsumerPolicy, UpdateableMixin

if TYPE_CHECKING:
    from django_compose.base.components.base_components import (
        Component,
        Context,
    )
    from django_compose.base.attributes import Attribute


T = TypeVar("T", bound="Modifier")
ModifierDict = OrderedDict[type[T], T]


class BaseModifier(Consumable):

    @abstractmethod
    def apply_before_build(self, context: Context, component: Component) -> None: ...

    @abstractmethod
    def apply(self, context: Context, component: Component) -> Component: ...


class Modifier(BaseModifier):

    @override
    def apply_before_build(self, context: Context, component: Component) -> None:
        """Injects behavior into the given component before the build process.

        It is safe to modify the component in place and return the same instance.
        It is also possible to return a new instance of the component if needed.
        """
        pass

    @override
    def apply(self, context: Context, component: Component) -> Component:
        """Injects behavior into the given component after the build process.

        It is safe to modify the component in place and return the same instance.
        It is also possible to return a new instance of the component if needed.
        """
        return component


class DeferredModifier(Modifier):
    """Since the referenced component is being saved, make sure to instantiate
    a new DeferredModifier for each use."""

    def __init__(self) -> None:
        self._deferred_context: Context | None = None
        self._deferred_component: Component | None = None

    @override
    def apply(self, context: Context, component: Component) -> Component:
        component = super().apply(context, component)
        self._deferred_context = context.copy()
        self._deferred_component = component
        return component

    def notify(self) -> None:
        if self._deferred_context is not None and self._deferred_component is not None:
            self.apply_when_notified(self._deferred_context, self._deferred_component)
        else:
            raise RuntimeError(
                """DeferredModifier.notify() called without prior apply().
Make sure you call super().apply() in overrides."""
            )

    @abstractmethod
    def apply_when_notified(self, context: Context, component: Component) -> None: ...


class PageRenderModifier(DeferredModifier):

    @override
    def apply(self, context: Context, component: Component) -> Component:
        component = super().apply(context, component)
        if not context.page:
            raise ValueError("No page found in context.")
        context.page.render_time_modifiers.append(self)
        return component


@final
class Modifiers(UpdateableMixin, BaseModifier):
    consumer_policy = ConsumerPolicy.ALL_CHILDREN

    def __init__(self, *modifiers: T) -> None:
        self.data: ModifierDict = OrderedDict()
        for modifier in modifiers:
            self.add(modifier)

    def values(self) -> ModifierDict:
        return OrderedDict(((m.key, m) for m in self.data.values()))

    def merge(self, other: Modifiers) -> Modifiers:
        merged = Modifiers(*self.data.values())
        merged.update(other, overwrite=True)
        return merged

    def add(self, modifier: T, overwrite=True) -> None:
        if overwrite or type(modifier) not in self.data:
            self.data[type(modifier)] = modifier

    @override
    def update(self, modifiers: Modifiers | Sequence[Modifier], overwrite=True) -> None:
        for modifier in modifiers:
            self.add(modifier, overwrite=overwrite)

    @override
    def apply_before_build(self, context: Context, component: Component) -> None:
        component._modifiers.update(self)

    @override
    def apply(self, context: Context, component: Component) -> Component:
        return component

    def __call__(self) -> Self:
        return self

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[Modifier]:
        return iter(self.data.values())

    def __contains__(self, item: type[T] | T) -> bool:
        if isinstance(item, type):
            return item in self.data
        return type(item) in self.data

    def __str__(self) -> str:
        return ", ".join(str(attr) for attr in self.data.values())

    def __bool__(self) -> bool:
        return bool(self.data)

    def __or__(self, other: Modifiers) -> Modifiers:
        return self.merge(other)

    def __ior__(self, other: Modifiers) -> Modifiers:
        self.update(other)
        return self


@final
class Attributes(UpdateableMixin, BaseModifier):
    consumer_policy = ConsumerPolicy.DIRECT_CHILDREN

    def __init__(self, *attributes: Attribute) -> None:
        self._data: OrderedDict[str, Attribute] = OrderedDict()
        for attr in attributes:
            self.add(attr)

    def values(self) -> dict[str, Any]:
        return {attr.name: attr.value for attr in self._data.values()}

    def merge(self, other: Attributes) -> Attributes:
        merged = Attributes(*self._data.values())
        merged.update(other, overwrite=True)
        return merged

    def add(self, attribute: Attribute, overwrite=True) -> None:
        if attribute.name not in self:
            self._data[attribute.name] = attribute
        elif overwrite:
            self._data[attribute.name] = self._data[attribute.name] | attribute
        else:
            self._data[attribute.name] = attribute | self._data[attribute.name]

    @override
    def update(
        self, attributes: "Attributes" | Sequence[Attribute], overwrite=True
    ) -> None:
        for attr in attributes:
            self.add(attr, overwrite=overwrite)

    @override
    def apply_before_build(self, context: Context, component: Component) -> None:
        component._attributes.update(self)

    @override
    def apply(self, context: Context, component: Component) -> Component:
        return component

    def __call__(self) -> Self:
        return self

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Attribute]:
        return iter(self._data.values())

    def __contains__(self, item: str | Attribute) -> bool:
        if isinstance(item, str):
            return item in self._data
        return item.name in self._data

    def __str__(self) -> str:
        return " ".join(str(attr) for attr in self._data.values())

    def __bool__(self) -> bool:
        return bool(self._data)

    def __or__(self, other: Attributes) -> Attributes:
        return self.merge(other)

    def __ior__(self, other: Attributes) -> Attributes:
        self.update(other)
        return self
