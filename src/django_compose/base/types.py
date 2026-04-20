from __future__ import annotations

from collections.abc import Callable, Sequence

from typing_extensions import TypeVar, TypeAlias, OrderedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from django_compose.base.attributes import Attribute, Attributes
    from django_compose.base.context import Context
    from django_compose.base.modifiers.base_modifiers import Modifier, Modifiers
    from django_compose.base.components import BaseComponent

T_BaseComponent = TypeVar("T_BaseComponent", bound="BaseComponent")

GenericComponentLike: TypeAlias = None | T_BaseComponent | Sequence[T_BaseComponent]
TemplateFunctionType: TypeAlias = Callable[[Context], "Children"]
GenericComponentChildren: TypeAlias = (
    None
    | str
    | T_BaseComponent
    | type[T_BaseComponent]
    | TemplateFunctionType
    | Sequence["GenericComponentChildren[T_BaseComponent]"]
)

ComponentLike: TypeAlias = GenericComponentLike["BaseComponent"]
Children: TypeAlias = GenericComponentChildren["BaseComponent"]

AttributeLike: TypeAlias = (
    None | str | Attribute | Attributes | Sequence["AttributeLike"]
)
ModifierLike: TypeAlias = None | Modifier | Modifiers | Sequence["ModifierLike"]
ModifiersOrAttributes: TypeAlias = (
    None
    | str
    | Attribute
    | Attributes
    | Modifier
    | Modifiers
    | Sequence["ModifiersOrAttributes"]
)

T_Modifier = TypeVar("T_Modifier", bound="Modifier")
ModifierDict = OrderedDict[type[T_Modifier], T_Modifier]

__all__ = [
    "GenericComponentLike",
    "TemplateFunctionType",
    "GenericComponentChildren",
    "ComponentLike",
    "Children",
    "AttributeLike",
    "ModifiersOrAttributes",
]
