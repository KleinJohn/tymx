from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, ClassVar, Self, TypeVar

from django_compose.base.helpers.base_model import BaseModel

if TYPE_CHECKING:
    from django_compose.base.context import Context, ContextFrame


T_Consumable = TypeVar("T_Consumable", bound="Consumable")


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

    def policy_applies(self, context: Context, frame: ContextFrame) -> bool:
        match self.consumer_policy:
            case ConsumerPolicy.NONE:
                return False
            case ConsumerPolicy.ALL_CHILDREN:
                return True
            case ConsumerPolicy.ALL_BUILT_CHILDREN:
                return context.data.component.builds_itself
            case ConsumerPolicy.DIRECT_CHILDREN:
                return frame.level == len(context.history) - 1
            case ConsumerPolicy.DIRECT_BUILT_CHILDREN:
                # we can't use current_depth here because there might be unbuilt components in
                # between, so we need to check all components between
                return all(
                    not frame.component.builds_itself
                    for frame in context.history[frame.level :]
                )
            case ConsumerPolicy.CUSTOM:
                return self.custom_policy(context, frame)

    def custom_policy(self, context: Context, frame: ContextFrame) -> bool:
        raise NotImplementedError()

    def merge(self: Self, other: Consumable) -> Self:
        """Overwrites by default."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"Cannot merge {self.__class__} with {other.__class__}")
        return other

    def merge_if_policy_applies(
        self: Self,
        other: Self | None,
        context: Context,
        frame: ContextFrame,
    ) -> Self:
        """Only override if you want to check if policy applies to parts of
        a collection of this consumable."""
        # this is not supposed to check whether the policy applies to the
        # consumable itself, but it is supposed to merge all collected consumables
        # to which the policy applies (the policy check on this is already done in get())
        if other is None:
            return self
        return self.merge(other)
