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
    "Applies only to the unbuilt component itself"

    ALL_CHILDREN = auto()
    "Applies to all children including unbuilt ones."

    DIRECT_CHILDREN = auto()
    "Applies only to direct children, including unbuilt ones."

    ALL_BUILT_CHILDREN = auto()
    "Applies to all built children (html components)."

    DIRECT_BUILT_CHILDREN = auto()
    "Applies only to the the first layer of built children under the applying component."

    CUSTOM = auto()
    "Calls the custom_policy method to determine applicability"

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

    def policy_applies(self, context_snapshot: ContextTraversalSnapshot) -> bool:
        # TODO: check if we need to adjust this, so that a full check is done
        # (since during_traversal assumes a break would have happened if needed)
        return self.policy_applies_during_traversal(context_snapshot)[0]

    def policy_applies_during_traversal(
        self,
        context_snapshot: ContextTraversalSnapshot,
    ) -> tuple[bool, bool]:
        """Returns a tuple of (can_consume, should_break)."""
        match self.consumer_policy:
            case ConsumerPolicy.NONE:
                return (False, True)
            case ConsumerPolicy.ALL_CHILDREN:
                return (True, False)
            case ConsumerPolicy.DIRECT_CHILDREN:
                return (True, True)
            case ConsumerPolicy.ALL_BUILT_CHILDREN:
                component = context_snapshot.context.current_component
                component_is_built = component.is_built if component else False
                return (component_is_built, False)
            case ConsumerPolicy.DIRECT_BUILT_CHILDREN:
                # assume it would have break'ed during traversal if one component in the path was not built
                component = context_snapshot.context.current_component
                component_is_built = component.is_built if component else False
                return (component_is_built, True)
            case ConsumerPolicy.CUSTOM:
                return self.custom_policy(context_snapshot)

    def custom_policy(
        self,
        context_snapshot: ContextTraversalSnapshot,
    ) -> tuple[bool, bool]:
        raise NotImplementedError()

    def merge(self: T_Consumable, other: T_Consumable) -> T_Consumable:
        """Overwrites by default."""
        return other

    def merge_if_policy_applies(
        self: T_Consumable,
        other: T_Consumable | None,
        context_snapshot: ContextTraversalSnapshot,
    ) -> T_Consumable:
        """Only override if you want to check if policy applies to parts of
        a collection of this consumable."""
        # this is not supposed to check whether the policy applies to the
        # consumable itself, but it is supposed to merge all collected consumables
        # to which the policy applies (the policy check on this is already done in get())
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


class ContextTraversalSnapshot:
    """A snapshot of a traversal through the context's data stack"""

    def __init__(
        self,
        context: Context,
        max_depth: int,
        current_depth: int,
        frame: ContextFrame,
    ) -> None:
        self.context = context
        self.max_depth = max_depth
        self.current_depth = current_depth
        self.frame = frame


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
        self.current_component: BaseComponent | None = None

    def copy(self) -> Context:
        return self.copy_with()

    def copy_with(self, **kwargs: Any) -> Context:
        router = kwargs.get("router", self.router)
        page = kwargs.get("page", self.page)
        data_stack: list[ContextFrame] | None = kwargs.get(
            "data_stack", self._data_stack
        )
        if data_stack is not None:
            data_stack = [*data_stack]
        return Context(router=router, page=page, data_stack=data_stack)

    def push_data(self, data: DataDict) -> None:
        assert self.current_component is not None
        self._data_stack.append(ContextFrame(self.current_component, data))

    def pop_frame(self) -> None:
        if not self._data_stack:
            raise IndexError("No provider to pop from the context.")
        self._data_stack.pop()

    def get(self, key: type[T_Consumable]) -> T_Consumable | None:
        assert self.current_component is not None
        if key.consumer_policy.is_built_only and not self.current_component.is_built:
            return None
        temp: T_Consumable | None = None
        depth = len(self._data_stack)
        for level in reversed(range(depth)):
            frame = self.get_frame(level)
            consumable = frame.get(key)
            snapshot = ContextTraversalSnapshot(
                context=self,
                max_depth=depth,
                current_depth=level,
                frame=frame,
            )
            if consumable is None:
                continue
            can_consume, should_break = consumable.policy_applies_during_traversal(
                snapshot
            )
            if should_break:
                break
            if not can_consume:
                continue
            temp = consumable.merge_if_policy_applies(temp, snapshot)
            if key.consume_first_matching:
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
