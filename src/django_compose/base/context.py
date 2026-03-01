from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, TypeAlias

from typing_extensions import Any, TypeVar

if TYPE_CHECKING:
    from django_compose.base import Page, Router
    from django_compose.base.components.base_components import BaseComponent


T_Consumable = TypeVar("T_Consumable", bound="Consumable")
DataDict: TypeAlias = dict[type[T_Consumable], T_Consumable]


class ConsumerPolicy(Enum):
    """Defines who can consume a Consumable."""

    NONE = auto()
    ALL_CHILDREN = auto()
    DIRECT_CHILDREN = auto()
    ALL_BUILT_CHILDREN = auto()
    DIRECT_BUILT_CHILDREN = auto()
    CUSTOM = auto()

    @property
    def is_direct(self) -> bool:
        return self in {
            ConsumerPolicy.DIRECT_CHILDREN,
            ConsumerPolicy.DIRECT_BUILT_CHILDREN,
        }

    @property
    def is_built_only(self) -> bool:
        return self in {
            ConsumerPolicy.ALL_BUILT_CHILDREN,
            ConsumerPolicy.DIRECT_BUILT_CHILDREN,
        }


class Consumable:
    consumer_policy = ConsumerPolicy.NONE
    consume_first_matching = True

    def policy_applies(
        self,
        context: Context,
        consumer: BaseComponent,
        consumer_level: int,
        self_level: int,
    ) -> bool:
        match self.consumer_policy:
            case ConsumerPolicy.NONE:
                return False
            case ConsumerPolicy.ALL_CHILDREN:
                return True
            case ConsumerPolicy.DIRECT_CHILDREN:
                return consumer_level == self_level + 1
            case ConsumerPolicy.ALL_BUILT_CHILDREN:
                return consumer.is_built
            case ConsumerPolicy.DIRECT_BUILT_CHILDREN:
                # true, if all frames between self and consumer are not renderable
                return all(
                    frame.component.is_built
                    for frame in context._data_stack[self_level + 1 : consumer_level]
                )
            case ConsumerPolicy.CUSTOM:
                return self.custom_policy(context, consumer, consumer_level, self_level)
        return False

    def custom_policy(
        self,
        context: Context,
        consumer: BaseComponent,
        consumer_level: int,
        self_level: int,
    ) -> bool:
        raise NotImplementedError()

    def merge(self: T_Consumable, other: T_Consumable) -> T_Consumable:
        """Overwrites by default."""
        return other

    def merge_if_policy_applies(
        self: T_Consumable,
        other: T_Consumable | None,
        context: Context,
        consumer: BaseComponent,
        consumer_level: int,
        self_level: int,
    ) -> T_Consumable:
        """Only override if you want to check if policy applies to parts of
        a collection of this consumable."""
        # this is not supposed to check whether the policy applies to the
        # consumable itself, but it is supposed to merge all collected consumables
        # to which the policy applies
        if other is None:
            return self
        return self.merge(other)


class ContextFrame:
    def __init__(self, component: BaseComponent, data: DataDict | None = None) -> None:
        self.component = component
        self.data = data if data is not None else {}

    def get(self, key: type[T_Consumable]) -> T_Consumable | None:
        return self.data.get(key)

    def __getitem__(self, key: type[T_Consumable]) -> T_Consumable:
        value = self.get(key)
        if value is None:
            raise KeyError(f"Key {key} not found in context frame.")
        return value

    def __setitem__(self, key: type[T_Consumable], value: T_Consumable) -> None:
        self.data[key] = value

    def __contains__(self, key: type[T_Consumable]) -> bool:
        return key in self.data


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
        self._data_stack: list[ContextFrame] = data_stack if data_stack is not None else []
        self.current: BaseComponent | None = None

    def copy(self) -> Context:
        return self.copy_with()

    def copy_with(self, **kwargs: Any) -> Context:
        router = kwargs.get("router", self.router)
        page = kwargs.get("page", self.page)
        data_stack: list[ContextFrame] | None = kwargs.get("data_stack", self._data_stack)
        if data_stack is not None:
            data_stack = [*data_stack]
        return Context(router=router, page=page, data_stack=data_stack)

    def push_data(self, data: DataDict) -> None:
        assert self.current is not None
        self._data_stack.append(ContextFrame(self.current, data))

    def pop_frame(self) -> None:
        if not self._data_stack:
            raise IndexError("No provider to pop from the context.")
        self._data_stack.pop()

    def get(self, key: type[T_Consumable]) -> T_Consumable | None:
        assert self.current is not None
        if (
            key.consumer_policy == ConsumerPolicy.NONE
            or key.consumer_policy.is_built_only
            and not self.current.is_built
        ):
            return None
        temp: T_Consumable | None = None
        depth = len(self._data_stack)
        for level in reversed(range(depth)):
            frame = self.get_frame(level)
            consumable = frame.get(key)
            can_consume = False
            # we could use consumable.policy_applies here
            # but we can optimize for early breaks this way
            match key.consumer_policy:
                case ConsumerPolicy.ALL_CHILDREN:
                    can_consume = True
                case ConsumerPolicy.DIRECT_CHILDREN:
                    can_consume = level == depth - 1
                case ConsumerPolicy.ALL_BUILT_CHILDREN:
                    can_consume = True
                case ConsumerPolicy.DIRECT_BUILT_CHILDREN:
                    if frame.component.is_built:
                        break
                    can_consume = True  # is_built checked above
                case ConsumerPolicy.CUSTOM:
                    can_consume = (
                        consumable.custom_policy(self, self.current, depth, level)
                        if consumable is not None
                        else False
                    )
            if not can_consume or consumable is None:
                continue
            temp = consumable.merge_if_policy_applies(temp, self, self.current, depth, level)
            if can_consume and key.consume_first_matching:
                break
        return temp

    def get_frame(self, level: int) -> ContextFrame:
        return self._data_stack[level]

    def __len__(self) -> int:
        return len(self._data_stack)

    def __str__(self) -> str:
        return str([[f.__name__ for f in s.data] for s in self._data_stack])

    @property
    def current_url(self) -> str:
        if not self.page:
            raise ValueError("No page found in context.")
        return self.router.routes[self.page.name].url
