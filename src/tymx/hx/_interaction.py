from inspect import ismethod
from typing import Callable

from attrs import field

from tymx.base.helpers.converters import enum_converter
from tymx.base.modifiers.base_modifiers import Modifier
from tymx.hx._helpers import HttpMethod
from tymx.hx._state import StateChange, Stateful


class Interaction(Modifier):
    method: HttpMethod = field(converter=enum_converter(HttpMethod))
    on: str | None = None
    target: str | None = None


def _get_stateful(callback: Callable[[], StateChange]) -> Stateful:
    stateful = getattr(callback, "__self__", None)
    if stateful is None and ismethod(callback):
        stateful = callback.__self__
    if not isinstance(stateful, Stateful):
        raise ValueError("Interaction callbacks must be bound to a Stateful's method.")
    return stateful


def interaction(
    callback: Callable[[], StateChange], on: str | None = None, method=HttpMethod.GET
) -> Interaction:
    stateful = _get_stateful(callback)
    # TODO: use stateful.__route__ to determine the target
    print(f"Interaction callback is bound to Stateful: {stateful}")
    return Interaction(on=on, method=method)


def on_click(callback: Callable[[], StateChange], method=HttpMethod.GET) -> Interaction:
    return interaction(callback, on="click", method=method)
