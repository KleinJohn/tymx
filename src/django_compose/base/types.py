from __future__ import annotations

from collections.abc import Callable, Sequence

from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from django_compose.base.attributes import Attribute, Attributes
    from django_compose.base.context import Context
    from django_compose.base.modifiers.base_modifiers import Modifier, Modifiers
    from django_compose.base.components import Component

_T = TypeVar("_T")
Registry = dict[type[_T], _T]

type BuildFunctionType = Callable[["Context"], "Children"]
type Children = (
    None | str | Component | type[Component] | BuildFunctionType | Sequence["Children"]
)

type ModifierLike = None | Modifier | Modifiers | Sequence[ModifierLike]
type AttributeLike = None | str | Attribute | Attributes | Sequence[AttributeLike]
type ModifiersOrAttributes = None | str | Attribute | Attributes | Modifier | Modifiers | Sequence[
    ModifiersOrAttributes
]

type ModifierDict = Registry[Modifier]

__all__ = [
    "BuildFunctionType",
    "Children",
    "AttributeLike",
    "ModifierLike",
    "ModifiersOrAttributes",
    "ModifierDict",
]
