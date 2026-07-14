from inspect import ismethod
from typing import Callable, ClassVar

from attrs import field

from tymx.base.consumable import ConsumerPolicy
from tymx.base.helpers.converters import enum_converter
from tymx.base.modifiers.base_modifiers import Modifier
from tymx.hx._helpers import HttpMethod
from tymx.hx._state import StateChange, Stateful


class Interaction(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.DIRECT_BUILT_CHILDREN

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
    route = stateful.__route__
    if route is None:
        route = f"/{stateful.__class__.__name__}/{callback.__name__}"
    return Interaction(on=on, method=method, target=route)


def on_click(callback: Callable[[], StateChange], method=HttpMethod.GET) -> Interaction:
    return interaction(callback, on="click", method=method)
