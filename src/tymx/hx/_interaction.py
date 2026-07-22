from collections.abc import Sequence
from inspect import ismethod
from typing import Any, Callable, ClassVar, override

from attrs import field

from tymx.base.components.base_components import Component
from tymx.base.consumable import ConsumerPolicy
from tymx.base.context import Context
from tymx.base.helpers.converters import enum_converter, string_type_converter
from tymx.base.modifiers.base_modifiers import Modifier
from tymx.base.attributes import Attribute
from tymx.hx._helpers import HttpMethod, HxSwap, HxSync, HxTrigger, SwapTarget
from tymx.hx._state import StateChange, Stateful
from tymx.hx import a


def _trigger_converter(
    value: str | HxTrigger | Sequence[HxTrigger | str] | None,
) -> str | None:
    if value is None:
        return None
    if isinstance(value, HxTrigger):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, Sequence):
        return ", ".join(str(v) for v in value)
    raise ValueError(f"Invalid trigger value: {value}")


class Interaction(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.DIRECT_BUILT_CHILDREN

    method: HttpMethod = field(converter=enum_converter(HttpMethod))
    route: str
    trigger: str | None = field(default=None, converter=_trigger_converter)
    target: str | None = None
    swap: str | None = field(
        default=None,
        converter=string_type_converter(HxSwap, optional=True),
    )
    sync: str | None = field(
        default=None,
        converter=string_type_converter(HxSync, optional=True),
    )
    swap_oob: bool | str | None = None
    select: str | None = None
    select_oob: str | None = None
    encoding: str | None = None
    confirm: str | None = None
    push_url: bool | None = None

    def get_attributes(self) -> list[Attribute]:
        attributes: list[Attribute] = []
        if self.method is not None:
            match self.method:
                case HttpMethod.GET:
                    attributes.append(a.hx_get(self.route))
                case HttpMethod.POST:
                    attributes.append(a.hx_post(self.route))
                case HttpMethod.PUT:
                    attributes.append(a.hx_put(self.route))
                case HttpMethod.DELETE:
                    attributes.append(a.hx_delete(self.route))
                case HttpMethod.PATCH:
                    attributes.append(a.hx_patch(self.route))
                case _:
                    raise ValueError(f"Invalid HTTP method: {self.method}")
        if self.trigger is not None:
            attributes.append(a.hx_trigger(self.trigger))
        if self.target is not None:
            attributes.append(a.hx_target(self.target))
        if self.swap is not None:
            attributes.append(a.hx_swap(self.swap))
        if self.sync is not None:
            attributes.append(a.hx_sync(self.sync))
        if self.swap_oob is not None:
            if isinstance(self.swap_oob, bool):
                attributes.append(a.hx_swap_oob("true" if self.swap_oob else "false"))
            else:
                attributes.append(a.hx_swap_oob(self.swap_oob))
        if self.select is not None:
            attributes.append(a.hx_select(self.select))
        if self.select_oob is not None:
            attributes.append(a.hx_select_oob(self.select_oob))
        if self.encoding is not None:
            attributes.append(a.hx_encoding(self.encoding))
        if self.confirm is not None:
            attributes.append(a.hx_confirm(self.confirm))
        if self.push_url is not None:
            attributes.append(a.hx_push_url("true" if self.push_url else "false"))
        return attributes

    @override
    def transform(self, context: Context, result: list[Component]) -> list[Component]:
        assert (
            len(result) == 1
        ), "Interaction modifier can only be applied to a single component"
        result[0] = result[0](self.get_attributes())
        return result


def _get_stateful(callback: Callable[[], StateChange[Any, Any]]) -> Stateful:
    stateful = getattr(callback, "__self__", None)
    if stateful is None and ismethod(callback):
        stateful = callback.__self__
    if not isinstance(stateful, Stateful):
        raise ValueError("Interaction callbacks must be bound to a Stateful's method.")
    return stateful


def interaction(
    callback: Callable[[], StateChange[Any, Any]],
    trigger: str | None = None,
    method=HttpMethod.GET,
    *,
    encoding: str | None = None,
    confirm: str | None = None,
    push_url: bool | None = None,
) -> Interaction:
    stateful = _get_stateful(callback)
    route = stateful.route(callback)
    return Interaction(
        method=method,
        route=route,
        trigger=trigger,
        encoding=encoding,
        confirm=confirm,
        push_url=push_url,
        swap=SwapTarget.OUTER,
        target=stateful.key.as_id(),
    )


def on_click(
    callback: Callable[[], StateChange[Any, Any]],
    method=HttpMethod.GET,
    *,
    encoding: str | None = None,
    confirm: str | None = None,
    push_url: bool | None = None,
) -> Interaction:
    return interaction(
        callback,
        trigger="click",
        method=method,
        encoding=encoding,
        confirm=confirm,
        push_url=push_url,
    )
