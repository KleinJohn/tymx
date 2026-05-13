from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from tymx.base.attributes import Attribute, Attributes
    from tymx.base.components import Component
    from tymx.base.context import Context
    from tymx.base.modifiers.base_modifiers import Modifier, Modifiers

_T = TypeVar("_T")
Registry = dict[type[_T], _T]

type BuildFunctionType = Callable[["Context"], "Children"]
type Children = None | str | Component | type[Component] | BuildFunctionType | Sequence[
    "Children"
]

type ModifierLike = None | Modifier | Modifiers | Sequence[ModifierLike]
type AttributeLike = None | str | Attribute | Attributes | Sequence[AttributeLike]
type ModifiersOrAttributes = (
    None
    | str
    | Attribute
    | Attributes
    | Modifier
    | Modifiers
    | Sequence[ModifiersOrAttributes]
)

type ModifierDict = Registry[Modifier]

__all__ = [
    "BuildFunctionType",
    "Children",
    "AttributeLike",
    "ModifierLike",
    "ModifiersOrAttributes",
    "ModifierDict",
]
