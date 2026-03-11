from __future__ import annotations

from dataclasses import dataclass, field, fields, replace
from enum import Enum, auto

from typing_extensions import Any, TypeVar, TYPE_CHECKING, Self, TypeAlias

if TYPE_CHECKING:
    from django_compose.base import Page, Router
    from django_compose.base.components.base_components import BaseComponent


T_Consumable = TypeVar("T_Consumable", bound="Consumable")


class DataDict(dict[type[T_Consumable], T_Consumable]):
    def get(self, key: type[T_Consumable]) -> T_Consumable | None:
        return super().get(key)

    def __getitem__(self, key: type[T_Consumable]) -> T_Consumable:
        value = self.get(key)
        if value is None:
            raise KeyError(f"Key {key} not found in data dict.")
        return value

    def __setitem__(self, key: type[T_Consumable], value: T_Consumable) -> None:
        super().__setitem__(key, value)
    
    def add(self, item: T_Consumable) -> None:
        self[item.__class__] = item


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
    consume_first_matching = False

    def policy_applies(self, context_snapshot: ContextTraversalSnapshot) -> bool:
        match self.consumer_policy:
            case ConsumerPolicy.NONE:
                return False
            case ConsumerPolicy.ALL_CHILDREN:
                return True
            case ConsumerPolicy.ALL_BUILT_CHILDREN:
                component = context_snapshot.context.current_component
                return component.is_built if component else False
            case ConsumerPolicy.DIRECT_CHILDREN:
                return context_snapshot.current_depth == context_snapshot.max_depth - 1
            case ConsumerPolicy.DIRECT_BUILT_CHILDREN:
                # we can't use current_depth here because there might be unbuilt components in
                # between, so we need to check all components between
                frames = context_snapshot.context._context_frames
                component = context_snapshot.context.current_component
                return all(
                    not frame.component.is_built
                    for frame in frames[context_snapshot.current_depth + 1 :]
                )
            case ConsumerPolicy.CUSTOM:
                return self.custom_policy(context_snapshot)

    def custom_policy(self, context_snapshot: ContextTraversalSnapshot) -> bool:
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
        context_frames: list[ContextFrame] | None = None,
    ) -> None:
        self.router = router
        self.page = page
        self._context_frames: list[ContextFrame] = (
            context_frames if context_frames is not None else []
        )
        self.current_component: BaseComponent | None = None

    def copy(self) -> Context:
        return self.copy_with()

    def copy_with(self, **kwargs: Any) -> Context:
        router = kwargs.get("router", self.router)
        page = kwargs.get("page", self.page)
        context_frames: list[ContextFrame] | None = kwargs.get(
            "context_frames", self._context_frames
        )
        if context_frames is not None:
            context_frames = [*context_frames]
        return Context(router=router, page=page, context_frames=context_frames)

    def push_data(self, data: DataDict) -> None:
        assert self.current_component is not None
        self._context_frames.append(ContextFrame(self.current_component, data))

    def pop_frame(self) -> None:
        if not self._context_frames:
            raise IndexError("No provider to pop from the context.")
        self._context_frames.pop()

    def get(self, key: type[T_Consumable]) -> T_Consumable | None:
        assert self.current_component is not None
        if key.consumer_policy.is_built_only and not self.current_component.is_built:
            return None
        temp: T_Consumable | None = None
        depth = len(self._context_frames)
        for level in reversed(range(depth)):
            frame = self.get_frame(level)
            consumable = frame.get(key)
            snapshot = ContextTraversalSnapshot(
                context=self,
                max_depth=depth,
                current_depth=level,
                frame=frame,
            )
            if consumable is None or not consumable.policy_applies(snapshot):
                continue
            temp = consumable.merge_if_policy_applies(temp, snapshot)
            if key.consume_first_matching:
                break
        return temp

    def get_frame(self, level: int) -> ContextFrame:
        return self._context_frames[level]

    def __len__(self) -> int:
        return len(self._context_frames)

    def __str__(self) -> str:
        return str([[f.__name__ for f in s.data] for s in self._context_frames])

    @property
    def current_url(self) -> str:
        if not self.page:
            raise ValueError("No page found in context.")
        return self.router.routes[self.page.name].url


@dataclass
class ContextData(Consumable):
    consumer_policy = ConsumerPolicy.ALL_CHILDREN
    overwrite_with_none: bool = field(default=False, kw_only=True)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "__dataclass_fields__" not in cls.__dict__:
            dataclass(cls)

    def __init__(
        self, *args: Any, overwrite_with_none: bool = False, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

    def merge(self, other: Self) -> Self:
        updates = {
            f.name: getattr(other, f.name)
            for f in fields(self)
            if getattr(other, f.name) is not None or other.overwrite_with_none
        }
        return replace(self, **updates)
