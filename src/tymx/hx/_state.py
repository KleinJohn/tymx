from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar, Self, TypeVar, override

from attrs import Factory, evolve, field, fields

import tymx.base.components.html_components as html

from tymx.base.components.base_components import Component, Text
from tymx.base.consumable import ConsumerPolicy
from tymx.base.context import Context
from tymx.base.helpers.base_model import BaseModel
from tymx.base.modifiers import Modifier, Modifiers, Key
from tymx.base.types import Children

_T = TypeVar("_T")


def state_converter(self: Stateful, key: str, default: _T) -> State[_T]:
    return State(type(self), key=key, value=default)


def state_field(default: _T, **kwargs) -> State[_T]:
    return field(
        default=Factory(
            lambda self: state_converter(self, "name", default), takes_self=True
        ),
        metadata={"is_state": True},
    )


class ComponentWrapper(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.NONE

    key: Key
    route_pattern: str

    @override
    def transform(self, context: Context, result: list[Component]) -> list[Component]:
        if not result:
            return result
        if len(result) == 1:
            component = result[0]
        else:
            component = html.Div(children=result)
        # context.router.register(f"{self.key}", component)
        return [component(self.key.as_attribute())]


class Stateful(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.ALL_CHILDREN
    __route__: ClassVar[str | None] = None
    __state_fields__: ClassVar[frozenset[str]]

    key: Key = field(factory=Key)

    def _as_value(self, context: Context) -> Self:
        stateful = context.get(self.__class__)
        if stateful is None:
            raise ValueError(
                f"Stateful component of type {self.__class__} not found in context"
            )
        return stateful

    def as_template(
        self, callback: Callable[[Context, Self], Children]
    ) -> Callable[[Context], Children]:
        return lambda context: callback(context, self._as_value(context))

    def route(self, callback: Callable) -> str:
        if self.__route__ is None:
            return f"/{self.__class__.__name__}/{callback.__name__}"
        return self.__route__

    @override
    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        for f in fields(type(self)):
            if f.metadata.get("is_state"):
                object.__setattr__(getattr(self, f.name), "_field_name", f.name)

    @override
    def on_use(self, context: Context) -> None:
        print(f"on_use called for {self.__class__.__name__} with key {self.key}")
        print(f"Parent: {context.parent.component}")

    @override
    def on_bind(self, context: Context) -> None:
        context.add(
            Modifiers(
                ComponentWrapper(key=self.key, route_pattern=self.route(self.on_bind))
            )
        )


class State[T](BaseModel, frozen=True):
    _stateful_t: type[Stateful] = field(kw_only=False, init=True, alias="stateful_t")
    _field_name: str = field(kw_only=False, init=True, alias="key")
    _value: T = field(kw_only=False, init=True, alias="value")

    def set(self, new_value: T) -> StateChange[T, T]:
        new_state = evolve(self, value=new_value)
        return StateChange(self, new_state)

    def _as_value(self, context: Context) -> T:
        stateful = context.get(self._stateful_t)
        if stateful is None:
            raise ValueError(
                f"Stateful component of type {self._stateful_t} not found in context"
            )
        return getattr(stateful, self._field_name)._value

    def as_text(
        self,
        transform: Callable[[T], str] = str,
    ) -> Callable[[Context], Text]:
        return lambda context: Text(text=transform(self._as_value(context)))

    def as_template(
        self, callback: Callable[[Context, T], Children]
    ) -> Callable[[Context], Children]:
        return lambda context: callback(context, self._as_value(context))


class StateChange[U, V](BaseModel, frozen=True):
    prev_state: State[U] = field(kw_only=False)
    next_state: State[V] = field(kw_only=False)
