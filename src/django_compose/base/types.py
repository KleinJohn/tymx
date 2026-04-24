from __future__ import annotations

from collections.abc import Callable, Sequence

from typing import (
    TypeVar,
    TypeAlias,
    TypeAliasType,
    OrderedDict,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from django_compose.base.attributes import Attribute, Attributes
    from django_compose.base.context import Context
    from django_compose.base.modifiers.base_modifiers import Modifier, Modifiers
    from django_compose.base.components import BaseComponent

T_BaseComponent = TypeVar("T_BaseComponent", bound="BaseComponent")

TemplateFunctionType: TypeAlias = Callable[["Context"], "Children"]
Children: TypeAlias = (
    None
    | str
    | BaseComponent
    | type[BaseComponent]
    | TemplateFunctionType
    | Sequence["Children"]
)

AttributeLike = TypeAliasType(
    "AttributeLike", "None | str | Attribute | Attributes | Sequence[AttributeLike]"
)
ModifierLike = TypeAliasType(
    "ModifierLike", "None | Modifier | Modifiers | Sequence[ModifierLike]"
)
ModifiersOrAttributes = TypeAliasType(
    "ModifiersOrAttributes",
    "None | str | Attribute | Attributes | Modifier | Modifiers | Sequence[ModifiersOrAttributes]",
)

T_Modifier = TypeVar("T_Modifier", bound="Modifier")
ModifierDict = OrderedDict[type[T_Modifier], T_Modifier]

__all__ = [
    "TemplateFunctionType",
    "Children",
    "AttributeLike",
    "ModifiersOrAttributes",
]
