from __future__ import annotations

from enum import Enum, auto

from typing import (
    Any,
    Self,
    TypeVar,
    TYPE_CHECKING,
    override,
    ClassVar,
)

from attrs import field, fields

from django_compose.base.helpers import BaseModel

if TYPE_CHECKING:
    from django_compose.base.components.base_components import BaseComponent


T_Consumable = TypeVar("T_Consumable", bound="Consumable")
_T = TypeVar("_T")


class DataDict(dict[type[T_Consumable], T_Consumable]):

    @override
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
    """
    Defines who can consume a Consumable.

    This enum specifies the scope and applicability of consumables within a component hierarchy.

    Attributes:
        NONE: Applies only to the unbuilt component itself.
        ALL_CHILDREN: Applies to all children including unbuilt ones.
        DIRECT_CHILDREN: Applies only to direct children, including unbuilt ones.
        ALL_BUILT_CHILDREN: Applies to all built children (html components).
        DIRECT_BUILT_CHILDREN: Applies only to the first layer of built children under the applying component.
        CUSTOM: Calls the custom_policy method to determine applicability.

    Properties:
        is_direct: Returns True if the policy applies only to direct children (DIRECT_CHILDREN or DIRECT_BUILT_CHILDREN).
        is_built_only: Returns True if the policy applies only to built children (ALL_BUILT_CHILDREN or DIRECT_BUILT_CHILDREN).
    """

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


class Consumable(BaseModel, frozen=True):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.NONE
    consume_first_matching: ClassVar[bool] = False

    @classmethod
    def of(cls: type[T_Consumable], context: Context) -> T_Consumable | None:
        return context.get(cls)

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

    def merge(self: Self, other: Self) -> Self:
        """Overwrites by default."""
        return other

    def merge_if_policy_applies(
        self: Self,
        other: Self | None,
        context_snapshot: ContextTraversalSnapshot,
    ) -> Self:
        """Only override if you want to check if policy applies to parts of
        a collection of this consumable."""
        # this is not supposed to check whether the policy applies to the
        # consumable itself, but it is supposed to merge all collected consumables
        # to which the policy applies (the policy check on this is already done in get())
        if other is None:
            return self
        return self.merge(other)


class ContextFrame(BaseModel, frozen=True):

    component: BaseComponent = field(kw_only=False)
    data: DataDict = field(factory=DataDict, kw_only=False)

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


class ContextTraversalSnapshot(BaseModel, frozen=True):
    """A snapshot of a traversal through the context's data stack"""

    context: Context
    max_depth: int
    current_depth: int
    frame: ContextFrame


class Context(BaseModel, frozen=True):
    """Context for building and rendering components."""

    router: Any = field(kw_only=False)
    page: Any | None = field(default=None, kw_only=False)
    _context_frames: list[ContextFrame] = field(factory=list)

    @property
    def current_component(self) -> BaseComponent:
        if not self._context_frames:
            raise ValueError("No component found in context.")
        return self._context_frames[-1].component

    def push(self, component: BaseComponent, data: DataDict) -> None:
        self._context_frames.append(ContextFrame(component=component, data=data))

    def pop_frame(self) -> None:
        if not self._context_frames:
            raise IndexError("No provider to pop from the context.")
        self._context_frames.pop()

    def get(self, key: type[T_Consumable]) -> T_Consumable | None:
        if not self._context_frames:
            return None
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

    def __bool__(self) -> bool:
        return bool(self._context_frames)

    @property
    def current_url(self) -> str:
        if not self.page:
            raise ValueError("No page found in context.")
        return self.router.routes[self.page.name].url


class ContextData(Consumable, frozen=True):

    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.ALL_CHILDREN
    overwrite_with_none: ClassVar[bool] = False

    @override
    def merge(self, other: Consumable) -> Self:
        """Overwrites all common fields by the fields of other."""
        merged = {f.name: getattr(self, f.name) for f in fields(self)}
        other_data = {f.name: getattr(other, f.name) for f in fields(other)}
        if not self.overwrite_with_none:
            other_data = {k: v for k, v in other_data.items() if v is not None}
        return self.__class__(**{**merged, **other_data})
