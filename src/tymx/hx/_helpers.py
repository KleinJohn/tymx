from enum import StrEnum
from typing import Literal

from tymx.base.helpers.base_model import BaseModel


class HttpMethod(StrEnum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


class SwapTarget(StrEnum):
    INNER = "innerHTML"
    OUTER = "outerHTML"
    AFTER_BEGIN = "afterbegin"
    BEFORE_BEGIN = "beforebegin"
    AFTER_END = "afterend"
    BEFORE_END = "beforeend"
    DELETE = "delete"
    NONE = "none"


class MouseEvent(StrEnum):
    CLICK = "click"
    DBLCLICK = "dblclick"
    MOUSEDOWN = "mousedown"
    MOUSEUP = "mouseup"
    MOUSEENTER = "mouseenter"
    MOUSELEAVE = "mouseleave"
    MOUSEOVER = "mouseover"
    MOUSEOUT = "mouseout"
    MOUSEMOVE = "mousemove"
    CONTEXTMENU = "contextmenu"
    WHEEL = "wheel"


class PointerEvent(StrEnum):
    POINTERDOWN = "pointerdown"
    POINTERUP = "pointerup"
    POINTERENTER = "pointerenter"
    POINTERLEAVE = "pointerleave"
    POINTERMOVE = "pointermove"
    POINTERCANCEL = "pointercancel"
    GOTPOINTERCAPTURE = "gotpointercapture"
    LOSTPOINTERCAPTURE = "lostpointercapture"


class KeyEvent(StrEnum):
    CHANGE = "change"
    INPUT = "input"
    SUBMIT = "submit"
    FOCUS = "focus"
    BLUR = "blur"
    KEYDOWN = "keydown"
    KEYUP = "keyup"


class WindowEvent(StrEnum):
    """htmx pseudo-events with no native DOM equivalent."""

    LOAD = "load"
    REVEALED = "revealed"
    INTERSECT = "intersect"


class EventModifier(BaseModel, init=False, frozen=True):
    modifier: str
    value: str | None = None

    def __init__(
        self,
        when: Literal["once", "changed", "consume"] | None = None,
        /,
        *,
        delay: str | None = None,
        throttle: str | None = None,
        from_: str | None = None,
        target: str | None = None,
        queue: Literal["first", "last", "all", "none"] | None = None,
        root: str | None = None,
        threshold: float | None = None,
    ) -> None:
        """Only one of the parameters should be provided at a time."""
        given = {
            "when": when,
            "delay": delay,
            "throttle": throttle,
            "from": from_,
            "target": target,
            "queue": queue,
            "root": root,
            "threshold": threshold,
        }
        given = {k: v for k, v in given.items() if v is not None}

        if len(given) != 1:
            raise ValueError(
                f"exactly one modifier must be provided, got {len(given)}: {list(given)}"
            )

        name, val = next(iter(given.items()))

        if name == "when":
            # bare word: "once" / "changed" / "consume"
            modifier, value = str(val), None
        else:
            modifier, value = name, str(val)

        object.__setattr__(self, "modifier", modifier)
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        if self.value is None:
            return self.modifier
        return f"{self.modifier}:{self.value}"


class HxTrigger(BaseModel, init=False, frozen=True):
    """See: https://htmx.org/attributes/hx-trigger/"""

    event: str
    filter_expr: str | None = None
    poll_interval: str | None = None
    modifiers: list[str] = []

    def __init__(
        self,
        event: MouseEvent | PointerEvent | KeyEvent | WindowEvent | str | None = None,
        modifiers: list[EventModifier | str] | None = None,
        *,
        every: str | None = None,
        filter: str | None = None,
    ):
        if event is not None and every is not None:
            raise ValueError("an event and `every` (polling) are mutually exclusive")
        if event is None and every is None:
            raise ValueError("must provide either an event or `every`")

        object.__setattr__(self, "event", str(event) if event is not None else "")
        object.__setattr__(self, "filter_expr", filter)
        object.__setattr__(self, "poll_interval", every)
        object.__setattr__(
            self, "modifiers", [str(mod) for mod in modifiers] if modifiers else []
        )

    def __str__(self) -> str:
        if self.poll_interval is not None:
            head = f"every {self.poll_interval}"
        else:
            head = (
                f"{self.event}[{self.filter_expr}]" if self.filter_expr else self.event
            )
        return " ".join([head, *self.modifiers])


class HxSwap(BaseModel, init=False, frozen=True):
    """See: https://htmx.org/attributes/hx-swap/"""

    target: str | None
    modifiers: list[str] = []

    def __init__(
        self,
        target: SwapTarget | str | None = None,
        /,
        *,
        transition: bool = False,
        ignore_title: bool = False,
        swap: str | None = None,
        settle: str | None = None,
        scroll: Literal["top", "bottom"] | None = None,
        scroll_element: str | None = None,
        show: Literal["top", "bottom", "none"] | None = None,
        show_element: str | None = None,
    ):
        if scroll_element and not scroll:
            raise ValueError("`scroll_element` requires `scroll` to be set")
        if show_element and not show:
            raise ValueError("`show_element` requires `show` to be set")

    def __str__(self) -> str:
        return (
            f"{self.target} {" ".join(self.modifiers)}"
            if self.modifiers
            else self.target
        )
