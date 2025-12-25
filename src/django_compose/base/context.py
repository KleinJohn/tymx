from __future__ import annotations
from abc import ABC
from enum import Enum, auto
from typing import TYPE_CHECKING, TypeVar, TypeAlias

if TYPE_CHECKING:
    from django_compose.base.app import Router, Page
    from django_compose.base.components.base_components import BaseComponent, Renderable


class ConsumerPolicy(Enum):
    """Defines who can consume a Consumable."""

    NONE = auto()
    ALL = auto()
    ALL_DIRECT = auto()
    RENDERABLES = auto()


class Consumable(ABC):
    consumer_policy = ConsumerPolicy.NONE

    def applies_to(self, consumer: BaseComponent, parent: BaseComponent) -> bool:
        match self.consumer_policy:
            case ConsumerPolicy.NONE:
                return False
            case ConsumerPolicy.ALL:
                return True
            case ConsumerPolicy.ALL_DIRECT:
                return True
            case ConsumerPolicy.RENDERABLES:
                return isinstance(consumer, Renderable)
        return False


T = TypeVar("T", bound="Consumable")
DataDict: TypeAlias = dict[type[T], T]


class ContextFrame:
    def __init__(self, data: DataDict):
        self.data = data


class Context:
    """Context for building and rendering components."""

    def __init__(
        self,
        router: Router,
        page: Page | None = None,
        data_stack: list[ContextFrame] | None = None,
    ) -> None:
        self.router = router
        self.page = page
        self._data_stack: list[ContextFrame] = (
            data_stack if data_stack is not None else []
        )

    def copy(self) -> "Context":
        return self.copy_with()

    def copy_with(self, **kwargs) -> "Context":
        router = kwargs.get("router", self.router)
        page = kwargs.get("page", self.page)
        data_stack: list[ContextFrame] | None = kwargs.get(
            "data_stack", self._data_stack
        )
        if data_stack is not None:
            data_stack = [*data_stack]
        return Context(router=router, page=page, data_stack=data_stack)

    def add_data_frame(self, data: DataDict) -> None:
        self._data_stack.append(ContextFrame(data))

    def pop_data_frame(self) -> None:
        if not self._data_stack:
            raise IndexError("No provider to pop from the context.")
        self._data_stack.pop()

    def get(self, key: type[T]) -> T | None:
        for frame in reversed(self._data_stack):
            if key in frame.data:
                return frame.data[key]
        return None

    @property
    def url(self) -> str:
        if not self.page:
            raise ValueError("No page found in context.")
        return self.router.routes[self.page.name].url
