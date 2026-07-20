from __future__ import annotations

from typing import ClassVar, TypeVar, override

from attrs import Factory, evolve, field, fields

import tymx.base.components.html_components as html

from tymx.base.components.base_components import Component
from tymx.base.consumable import ConsumerPolicy
from tymx.base.context import Context
from tymx.base.helpers.base_model import BaseModel
from tymx.base.modifiers import Modifier, Modifiers, Key

_T = TypeVar("_T")


def state_converter(self: Stateful, key: str, default: _T) -> State[_T]:
    return State(type(self), key=key, value=default)


def state_field(**kwargs):
    return field(
        default=Factory(
            lambda self: state_converter(self, "name", "Initial Name"), takes_self=True
        ),
        metadata={"is_state": True},
    )


class ComponentWrapper(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.NONE

    key: Key

    @override
    def transform(self, result: list[Component]) -> list[Component]:
        if not result:
            return result
        if len(result) == 1:
            component = result[0]
        else:
            component = html.Div(children=result)
        # TODO: register component in context.router
        return [component(self.key.as_attribute())]


class Stateful(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.ALL_CHILDREN
    __route__: ClassVar[str | None] = None
    __state_fields__: ClassVar[frozenset[str]]

    key: Key = field(factory=Key)

    @override
    def __attrs_post_init__(self) -> None:
        for f in fields(type(self)):
            if f.metadata.get("is_state"):
                object.__setattr__(getattr(self, f.name), "_field_name", f.name)

    @override
    def on_bind(self, context: Context) -> None:
        context.add(Modifiers(ComponentWrapper(key=self.key)))


class State[T](BaseModel, frozen=True):
    _stateful_t: type[Stateful] = field(kw_only=False, init=True, alias="stateful_t")
    _field_name: str = field(kw_only=False, init=True, alias="key")
    _value: T = field(kw_only=False, init=True, alias="value")

    def set(self, new_value: T) -> StateChange[T, T]:
        new_state = evolve(self, value=new_value)
        return StateChange(self, new_state)

    def value(self, context: Context) -> T:
        stateful = context.get(self._stateful_t)
        if stateful is None:
            raise ValueError(
                f"Stateful component of type {self._stateful_t} not found in context"
            )
        return getattr(stateful, self._field_name)._value

    def __str__(self) -> str:
        return str(self._value)


class StateChange[U, V](BaseModel, frozen=True):
    prev_state: State[U] = field(kw_only=False)
    next_state: State[V] = field(kw_only=False)
