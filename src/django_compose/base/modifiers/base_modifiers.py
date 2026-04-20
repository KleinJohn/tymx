from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import TYPE_CHECKING, Annotated, cast

from pydantic import BeforeValidator, ConfigDict, Field
from typing_extensions import (
    Self,
    ClassVar,
    override,
)

from django_compose.base.components.base_components import BaseComponent
from django_compose.base.types import (
    ModifierDict,
    ModifierLike,
    T_Modifier,
)

from django_compose.base.context import (
    Consumable,
    ConsumerPolicy,
    ContextTraversalSnapshot,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from django_compose.base.components import BuildData


class BaseModifier(Consumable, ABC):
    @abstractmethod
    def apply(self, build: BuildData) -> None: ...
    @abstractmethod
    def transform(self, result: list[BaseComponent]) -> None: ...

    def __str__(self) -> str:
        return self.__class__.__name__


class Modifier(BaseModifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.ALL_CHILDREN

    @override
    def apply(self, build: BuildData) -> None:
        """Injects behavior into the given component before the build process.

        It is safe to modify the component in place and return the same instance.
        It is also possible to return a new instance of the component if needed.
        """
        pass

    @override
    def transform(self, result: list[BaseComponent]) -> None:
        """Injects behavior into the given component after the build process.

        It is safe to modify the component in place and return the same instance.
        It is also possible to return a new instance of the component if needed.
        """
        pass


def _convert_to_modifier_dict(modifiers: ModifierLike) -> ModifierDict:
    def match_modifiers_recursive(
        modifier: ModifierLike, mod_dict: ModifierDict
    ) -> None:
        match modifier:
            case None:
                return
            case Modifier():
                mod_dict[type(modifier)] = modifier
            case Modifiers():
                mod_dict.update(modifier._data)
            case Sequence():
                for item in modifier:
                    match_modifiers_recursive(item, mod_dict)
            case _:
                raise ValueError("Invalid modifier type.")

    mod_dict: ModifierDict = OrderedDict()
    match_modifiers_recursive(modifiers, mod_dict)
    return mod_dict


class Modifiers(BaseModifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.ALL_CHILDREN
    consume_first_matching: ClassVar[bool] = False

    _ut_data: Annotated[ModifierLike, BeforeValidator(_convert_to_modifier_dict)] = (
        Field(alias="modifiers", init=True, default=None, kw_only=False)
    )

    @property
    def _data(self) -> ModifierDict:
        return cast(ModifierDict, self._ut_data)

    def values(self) -> ModifierDict:
        return OrderedDict(self._data)

    def add(self, modifier: Modifier, overwrite: bool = True) -> None:
        if overwrite or type(modifier) not in self._data:
            self._data[type(modifier)] = modifier

    def update(self, modifiers: ModifierLike, overwrite: bool = True) -> None:
        mod_dict = _convert_to_modifier_dict(modifiers)
        for mod in mod_dict.values():
            self.add(mod, overwrite=overwrite)

    @override
    def merge(self, other: Modifiers) -> Modifiers:
        """Merges with other by overwriting with other's modifiers."""
        if not isinstance(other, Modifiers):
            raise TypeError("Modifiers can only be merged with other Modifiers.")
        return self.__class__([self, other])

    @override
    def merge_if_policy_applies(
        self: Modifiers,
        other: Modifiers | None,
        context_snapshot: ContextTraversalSnapshot,
        overwrite: bool = True,
    ) -> Modifiers:
        if other is None:
            return Modifiers(
                # only include modifiers which can be consumed -> [0]
                *(m for m in self if m.policy_applies(context_snapshot))
            )
        merged = self.copy()
        for modifier in other:
            if modifier.policy_applies(context_snapshot):
                merged.add(modifier)
        return merged

    @override
    def apply(self, build: BuildData) -> None:
        pass

    @override
    def transform(self, build: BuildData) -> None:
        pass

    def copy(self) -> Self:
        return self.__class__(self)

    def __call__(self) -> Self:
        return self

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Modifier]:
        return iter(self._data.values())

    def __contains__(self, item: type[T_Modifier] | T_Modifier) -> bool:
        if isinstance(item, type):
            return item in self._data
        return type(item) in self._data

    def __str__(self) -> str:
        return ", ".join(str(attr) for attr in self._data.values())

    def __bool__(self) -> bool:
        return bool(self._data)

    def __or__(self, other: Modifiers) -> Modifiers:
        return self.merge(other)

    def __ior__(self, other: Modifiers) -> Modifiers:
        self.update(other)
        return self


class FrozenModifiers(Modifiers):
    model_config = ConfigDict(frozen=True)

    def add(self, modifier: Modifier, overwrite: bool = True) -> None:
        raise TypeError("FrozenModifiers cannot be modified.")

    def update(self, modifiers: ModifierLike, overwrite: bool = True) -> None:
        raise TypeError("FrozenModifiers cannot be modified.")
