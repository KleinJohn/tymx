from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import (
    TYPE_CHECKING,
    Any,
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
    from tymx.base.app import AbstractRoute, AbstractRouter


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
    component: Component
    _data: DataDict = field(alias="data", factory=DataDict)
    level: int

    def get(self, key: type[T_Consumable]) -> T_Consumable | None:
        return self._data.get(key)

    @property
    def attributes(self) -> Attributes | None:
        return self._data.get(Attributes)

    @attributes.setter
    def attributes(self, value: Attributes) -> None:
        self._data[Attributes] = value

    @property
    def modifiers(self) -> Modifiers | None:
        return self._data.get(Modifiers)

    @modifiers.setter
    def modifiers(self, value: Modifiers) -> None:
        self._data[Modifiers] = value

    @property
    def data(self) -> DataDict:
        return self._data

    def copy(self) -> Self:
        return self.__class__(
            component=self.component,
            data=self._data.copy(),
            level=self.level,
        )

    def __getitem__(self, key: type[T_Consumable]) -> T_Consumable:
        value = self.get(key)
        if value is None:
            raise KeyError(f"Key {key} not found in context frame.")
        return value

    def __setitem__(self, key: type[T_Consumable], value: T_Consumable) -> None:
        self._data[key] = value

    def __contains__(self, key: type[T_Consumable]) -> bool:
        return key in self._data

    def __str__(self) -> str:
        return str([f.__name__ for f in self._data.keys()])


class Context(BaseModel):
    """Context for building and rendering components."""

    router: AbstractRouter = field(kw_only=False)
    route: AbstractRoute
    history: list[ContextFrame] = field(factory=list)
    _data: ContextFrame | None = field(default=None, init=False)

    @property
    def data(self) -> ContextFrame:
        if self._data is None:
            raise ValueError("No data found in context.")
        return self._data

    @property
    def parent(self) -> Component | None:
        if not self.history:
            return None
        return self.history[-1].component

    @contextmanager
    def frame(self, provide_data: DataDict) -> Generator[None, None, None]:
        saved_data = self._data
        frame = evolve(self.data, data=provide_data)
        self._data = None
        self.push_frame(frame)
        try:
            yield
        finally:
            self.pop_frame()
            self._data = saved_data

    def push_frame(self, frame: ContextFrame) -> None:
        self.history.append(frame)

    def pop_frame(self) -> None:
        self.history.pop()

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

    def use(self, key: type[T_Consumable] | T_Consumable) -> T_Consumable:
        """Injects the consumable into the context and returns it."""
        consumable = key if isinstance(key, Consumable) else key()
        self.data[consumable.__class__] = consumable
        return consumable

    def bind(self, key: type[T_Consumable]) -> T_Consumable:
        """Retrieves the consumable, binds it to the context and returns it."""
        consumable = self.get(key)
        if consumable is None:
            raise ValueError(f"Consumable of type {key} not found in context.")
        consumable.on_bind(self)
        return consumable

    def copy(self) -> Self:
        res = self.__class__(
            router=self.router,
            route=self.route,
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

    @property
    def current_url(self) -> str:
        return self.router.get_url(self.route)


class ContextData(Consumable, frozen=True):
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
