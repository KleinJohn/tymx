from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Self,
    override,
)

from attrs import evolve, field, fields

from tymx.base.attributes.base_attributes import Attributes
from tymx.base.consumable import Consumable, ConsumerPolicy, T_Consumable
from tymx.base.helpers import BaseModel
from tymx.base.modifiers.base_modifiers import Modifiers

if TYPE_CHECKING:
    from tymx.base.components.base_components import Component
    from tymx.base.app import AbstractRouter


class DataDict(dict[type[T_Consumable], T_Consumable]):
    @override
    def __getitem__(self, key: type[T_Consumable]) -> T_Consumable:
        value = self.get(key)
        if value is None:
            raise KeyError(f"Key {key} not found in data dict.")
        return value

    @override
    def __setitem__(self, key: type[T_Consumable], value: T_Consumable) -> None:
        super().__setitem__(key, value)

    @override
    def copy(self) -> Self:
        return self.__class__(super().copy())

    def add(self, item: T_Consumable) -> None:
        self[item.__class__] = item


class ContextFrame(BaseModel):
    """
    The component_data is the data used to build the component.
    The inherited_data is the data which can be inherited by child components.
    """

    component: Component
    _component_data: DataDict = field(alias="data", factory=DataDict)
    _inherited_data: DataDict = field(alias="inherited_data", factory=DataDict)
    level: int

    def get(self, key: type[T_Consumable]) -> T_Consumable | None:
        return self._inherited_data.get(key)

    @property
    def attributes(self) -> Attributes | None:
        return self._component_data.get(Attributes)

    @attributes.setter
    def attributes(self, value: Attributes) -> None:
        self._component_data[Attributes] = value

    @property
    def modifiers(self) -> Modifiers | None:
        return self._component_data.get(Modifiers)

    @modifiers.setter
    def modifiers(self, value: Modifiers) -> None:
        self._component_data[Modifiers] = value

    def copy(self) -> Self:
        return self.__class__(
            component=self.component,
            data=self._component_data.copy(),
            inherited_data=self._inherited_data.copy(),
            level=self.level,
        )

    def add(self, item: Consumable, key: type[Consumable] | None = None) -> None:
        if key is None:
            key = item.__class__
        if key in self._component_data:
            self._component_data[key] = self._component_data[key].merge(item)
        else:
            self._component_data[key] = item

    def provide(self, item: Consumable, key: type[Consumable] | None = None) -> None:
        if key is None:
            key = item.__class__
        if key in self._inherited_data:
            self._inherited_data[key] = self._inherited_data[key].merge(item)
        else:
            self._inherited_data[key] = item

    def __getitem__(self, key: type[T_Consumable]) -> T_Consumable:
        value = self.get(key)
        if value is None:
            raise KeyError(f"Key {key} not found in context frame.")
        return value

    def __contains__(self, key: type[T_Consumable]) -> bool:
        return key in self._component_data

    def __str__(self) -> str:
        data = str([f.__name__ for f in self._component_data.keys()])
        inherited_data = str([f.__name__ for f in self._inherited_data.keys()])
        return f"ContextFrame(component={self.component.__class__.__name__}, level={self.level}, data={data}, inherited_data={inherited_data})"


class Context(BaseModel):
    """Context for building and rendering components."""

    router: AbstractRouter = field(kw_only=False)
    history: list[ContextFrame] = field(factory=list)
    _data: ContextFrame | None = field(default=None, init=False)

    @property
    def data(self) -> ContextFrame:
        if self._data is None:
            raise ValueError("No data found in context.")
        return self._data

    @property
    def parent(self) -> ContextFrame | None:
        if not self.history:
            return None
        return self.history[-1]

    @contextmanager
    def frame(self) -> Generator[None, None, None]:
        self.push_frame(self.data)
        self._data = None  # prevent calling context.data on instance in history
        try:
            yield
        finally:
            self._data = self.pop_frame()

    def push_frame(self, frame: ContextFrame) -> None:
        self.history.append(frame)

    def pop_frame(self) -> ContextFrame:
        return self.history.pop()

    def create_data(self, component: Component) -> None:
        self._data = ContextFrame(component=component, level=len(self.history))

    def get(self, key: type[T_Consumable]) -> T_Consumable | None:
        if not self.history or not self._data:
            return None
        if key.consumer_policy.is_built_only and not self.data.component.builds_itself:
            return None
        accumulated: T_Consumable | None = None
        for frame in reversed(self.history):
            consumable = frame.get(key)
            if consumable is None or not consumable.policy_applies(self, frame):
                continue
            accumulated = consumable.merge_if_policy_applies(accumulated, self, frame)
            if key.consume_first_matching:
                break
        return accumulated

    def use(self, item: type[T_Consumable] | T_Consumable) -> T_Consumable:
        """Provides the consumable and instantiates it if necessary, then returns it.
        Notifies the consumable's on_use() method."""
        consumable = item if isinstance(item, Consumable) else item()
        self.provide(consumable)
        consumable.on_use(self)
        return consumable

    def bind(self, key: type[T_Consumable]) -> T_Consumable:
        """Retrieves the consumable and returns it.
        Notifies the consumable's on_bind() method."""
        consumable = self.get(key)
        if consumable is None:
            raise ValueError(f"Consumable of type {key} not found in context.")
        consumable.on_bind(self)
        return consumable

    def consume(
        self,
        key: type[T_Consumable],
        default: T_Consumable | None = None,
        merge: T_Consumable | None = None,
    ) -> None:
        """Retrieves the consumable from the history, uses default if not found, then
        merges with the given item, if supplied, and adds it to the current frame.

        `context.consume(Attributes, default=Attributes(), merge=self.attributes)`

        is equivalent to:

        `inherited_attributes = context.get(Attributes) or Attributes()`<br>
        `context.data.add(inherited_attributes | self.attributes, key=Attributes)`
        """
        inherited_consumable = self.get(key)
        consumable = (
            inherited_consumable if inherited_consumable is not None else default
        )
        if consumable is None:
            return
        if merge is not None:
            consumable = consumable.merge(merge)
        self.data.add(consumable, key=key)

    def provide(self, item: Consumable, key: type[Consumable] | None = None) -> None:
        """Adds the consumable to the current frame to be inherited by child components."""
        self.data.provide(item, key=key)

    def add(self, item: Consumable, key: type[Consumable] | None = None) -> None:
        """Adds the consumable to the current frame to be used by the current component."""
        self.data.add(item, key=key)

    # def update_inherited(
    #     self, key: type[T_Consumable], modifier: Callable[[T_Consumable], T_Consumable]
    # ) -> bool:
    #     """Modifies the consumable in the current frame to be inherited by child components."""
    #     for frame in reversed(self.history):
    #         if key in frame._inherited_data:
    #             frame._inherited_data[key] = modifier(frame._inherited_data[key])
    #             return True
    #     return False

    def copy(self) -> Self:
        res = self.__class__(
            router=self.router,
            history=[frame.copy() for frame in self.history],
        )
        if self._data:
            res._data = self._data.copy()
        return res

    def __len__(self) -> int:
        return len(self.history)

    def __str__(self) -> str:
        c_name = self._data.component.__class__.__name__ if self._data else None
        return f"Context(current={c_name}, history={[str(s) for s in self.history]})"

    def __bool__(self) -> bool:
        return bool(self.history)


class ContextData(Consumable, frozen=True):  # type: ignore
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.ALL_CHILDREN
    overwrite_with_none: ClassVar[bool] = False

    @override
    def merge(self, other: Consumable) -> Self:
        """Overwrites all common fields by the fields of other."""
        merged = {f.name: getattr(self, f.name) for f in fields(self)}
        other_data = {f.name: getattr(other, f.name) for f in fields(other)}
        if not self.overwrite_with_none:
            other_data = {k: v for k, v in other_data.items() if v is not None}
        return self.__class__(**{**merged, **other_data})
