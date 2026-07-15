from __future__ import annotations

from typing import ClassVar, TypeVar, override

from attrs import evolve, field

from tymx.base.consumable import ConsumerPolicy
from tymx.base.context import Context
from tymx.base.helpers.base_model import BaseModel
from tymx.base.modifiers.base_modifiers import Modifier, Modifiers

_T = TypeVar("_T")


def state_converter(default: _T) -> State[_T]:
    return State(value=default)


class ComponentStateWrapper(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.DIRECT_BUILT_CHILDREN


class Stateful(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.ALL_CHILDREN
    __route__: ClassVar[str | None] = None

    @override
    def on_bind(self, context: Context) -> None:
        assert (
            context.data.modifiers is not None
        ), "Context data modifiers should not be None"
        context.provide(Modifiers([ComponentStateWrapper()]))


class State[T](BaseModel, frozen=True):
    value: T = field(kw_only=False)

    def set(self, new_value: T) -> StateChange[T, T]:
        new_state = evolve(self, value=new_value)
        return StateChange(self, new_state)

    def __str__(self) -> str:
        return str(self.value)


class StateChange[U, V](BaseModel, frozen=True):
    prev_state: State[U] = field(kw_only=False)
    next_state: State[V] = field(kw_only=False)
