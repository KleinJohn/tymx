from __future__ import annotations

from typing import ClassVar, TypeVar

from attrs import evolve, field

from tymx.base.consumable import ConsumerPolicy
from tymx.base.helpers.base_model import BaseModel
from tymx.base.modifiers.base_modifiers import Modifier

_T = TypeVar("_T")


def state_converter(default: _T) -> State[_T]:
    return State(value=default)


class Stateful(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.NONE
    __route__: ClassVar[str | None] = None


class State[T](BaseModel):
    value: T = field(kw_only=False)

    def set(self, new_value: T) -> StateChange[T, T]:
        new_state = evolve(self, value=new_value)
        return StateChange(self, new_state)


class StateChange[U, V](BaseModel):
    prev_state: State[U] = field(kw_only=False)
    next_state: State[V] = field(kw_only=False)
