from __future__ import annotations

from abc import abstractmethod
from collections import OrderedDict
from collections.abc import Sequence
from typing import TYPE_CHECKING, Iterator, ClassVar, Self, override

from attrs import evolve, field

from django_compose.base.consumable import Consumable, ConsumerPolicy
from django_compose.base.types import (
    ModifierDict,
    ModifierLike,
)

if TYPE_CHECKING:
    from django_compose.base.components import BaseComponent
    from django_compose.base.context import Context, ContextTraversalSnapshot


# We need BaseModifiers so that we can ensure that you can't have Modifiers inside Modifiers
class BaseModifier(Consumable, frozen=False):  # type: ignore
    """Defines the interface for applying modifications to components during the build process."""

    @abstractmethod
    def apply(self, context: Context) -> None: ...
    @abstractmethod
    def transform(self, result: list[BaseComponent]) -> list[BaseComponent]: ...

    def __str__(self) -> str:
        return self.__class__.__name__


class Modifier(BaseModifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.ALL_CHILDREN

    @override
    def apply(self, context: Context) -> None:
        pass

    @override
    def transform(self, result: list[BaseComponent]) -> list[BaseComponent]:
        return result

    def __str__(self) -> str:
        return self.__class__.__name__


def _convert_to_modifier_dict(modifiers: ModifierLike) -> ModifierDict:
    def match_modifiers_recursive(modifier: ModifierLike, mod_dict: ModifierDict) -> None:
        match modifier:
            case None:
                return
            case Modifier():
                mod_dict[type(modifier)] = modifier
            case Modifiers():
                mod_dict.update(modifier._modifiers)
            case Sequence():
                for item in modifier:
                    match_modifiers_recursive(item, mod_dict)
            case _:
                raise ValueError("Invalid modifier type.")

    mod_dict: ModifierDict = OrderedDict()
    match_modifiers_recursive(modifiers, mod_dict)
    return mod_dict


class Modifiers(BaseModifier, frozen=False):

    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.ALL_CHILDREN
    consume_first_matching: ClassVar[bool] = False

    _modifiers: ModifierDict = field(
        alias="modifiers",
        converter=_convert_to_modifier_dict,
        kw_only=False,
        default=None,
    )

    def values(self) -> ModifierDict:
        return OrderedDict(self._modifiers)

    def add(self, modifier: Modifier, overwrite: bool = True) -> None:
        if overwrite or type(modifier) not in self._modifiers:
            self._modifiers[type(modifier)] = modifier

    def update(self, modifiers: ModifierLike, overwrite: bool = True) -> None:
        mod_dict = _convert_to_modifier_dict(modifiers)
        for mod in mod_dict.values():
            self.add(mod, overwrite=overwrite)

    @override
    def merge(self, other: Consumable) -> Self:
        """Merges with other by overwriting with other's modifiers."""
        if not isinstance(other, Modifiers):
            raise TypeError("Can only merge with another Modifiers instance.")
        return evolve(self, modifiers=[self, other])

    @override
    def merge_if_policy_applies(
        self,
        other: Consumable | None,
        context_snapshot: ContextTraversalSnapshot,
        overwrite: bool = True,
    ) -> Self:
        if not isinstance(other, Modifiers) and other is not None:
            raise TypeError("Can only merge with another Modifiers instance.")
        if other is None:
            return self.__class__(
                # only include modifiers which can be consumed -> [0]
                [m for m in self if m.policy_applies(context_snapshot)],
            )
        merged = self.copy()
        for modifier in other:
            if modifier.policy_applies(context_snapshot):
                merged.add(modifier)
        return merged

    @override
    def apply(self, context: Context) -> None:
        pass

    @override
    def transform(self, result: list[BaseComponent]) -> list[BaseComponent]:
        return result

    def copy(self) -> Self:
        """Creates a copy of this Modifiers (deep copy)"""
        return evolve(self, modifiers=self._modifiers)

    def __call__(self) -> Self:
        return self

    def __len__(self) -> int:
        return len(self._modifiers)

    def __iter__(self) -> Iterator[Modifier]:
        return iter(self._modifiers.values())

    def __contains__(self, item: type[Modifier] | Modifier) -> bool:
        if isinstance(item, type):
            return item in self._modifiers
        return type(item) in self._modifiers

    def __str__(self) -> str:
        return ", ".join(str(attr) for attr in self._modifiers.values())

    def __bool__(self) -> bool:
        return bool(self._modifiers)

    def __or__(self, other: Modifiers) -> Modifiers:
        return self.merge(other)

    def __ior__(self, other: Modifiers) -> Modifiers:
        self.update(other)
        return self


class FrozenModifiers(Modifiers, frozen=True):  # type: ignore

    def add(self, modifier: Modifier, overwrite: bool = True) -> None:
        raise TypeError("FrozenModifiers cannot be modified.")

    def update(self, modifiers: ModifierLike, overwrite: bool = True) -> None:
        raise TypeError("FrozenModifiers cannot be modified.")
