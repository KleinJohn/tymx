from __future__ import annotations

from abc import abstractmethod
from collections import OrderedDict
from collections.abc import Callable, Iterable, Iterator, Sequence, KeysView, ValuesView
from typing import TYPE_CHECKING, Any, Self, override

from attrs import evolve, field

from tymx.base.consumable import Consumable, ConsumerPolicy
from tymx.base.helpers import BaseModel
from tymx.base.modifiers import BaseModifier
from tymx.base.types import AttributeLike

if TYPE_CHECKING:
    from tymx.base.components.base_components import Component
    from tymx.base.context import Context


def _clean_kwargs(
    kwarg_dict: dict[str, Any], underscores_to_hyphens: bool = True
) -> OrderedDict[str, Any]:
    cleaned_kwargs: OrderedDict[str, str] = OrderedDict()
    for key, value in kwarg_dict.items():
        clean_key = key
        clean_value = value
        if underscores_to_hyphens:
            clean_key = clean_key.replace("_", "-")
        cleaned_kwargs[clean_key] = clean_value
    return cleaned_kwargs


class Attribute[T](BaseModel, frozen=True):
    """A modifier which adds attributes to a Component.

    A Attribute can hold multiple attribute values, which can be set when the Attribute is called.
    The default value for each attribute is an empty string.
    """

    name: str = field(kw_only=False)
    value: T | None = None

    def __call__(self, value: T | None = None, **kwargs: Any) -> Self:
        """Assigns values to the attributes.

        The values are assigned to the attributes in the order they were defined.
        Leave a value as None to keep the current value for that attribute.
        If fewer values are provided than attributes, the remaining attributes keep their current values.
        Overrides of this method should call their parent's __call__ method.
        """
        return evolve(self, value=value, **kwargs)

    def __or__(self, other: Self) -> Self:
        return self.merge(other)

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, Attribute):
            return self == item
        return item == self.value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Attribute):
            return NotImplemented
        return self.name == other.name and self.value == other.value

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()

    def merge(self, other: Attribute) -> Self:
        """Default behavior is to override own value with the other attribute's value."""
        if self.name != other.name:
            raise ValueError(
                f"Cannot merge attributes with different names: {self.name} and {other.name}"
            )
        return evolve(self, value=other.value)

    def merge_all(self, attributes: Iterable[Self]) -> Self:
        merged = self
        for attr in attributes:
            merged = merged | attr
        return merged


class SimpleAttribute(Attribute[str], frozen=True):
    value: str | None = None

    def __call__(self, value: str | None = None, **kwargs: Any) -> Self:
        return super().__call__(value, **kwargs)

    def __str__(self) -> str:
        if self.value is None:
            return ""
        return f'{self.name}="{self.value}"'


class BooleanAttribute(Attribute[bool], frozen=True):
    """A modifier which adds a boolean attribute to a Component.

    The attribute is included when the value is True, and omitted when the value is False.
    """

    value: bool | None = None
    use_true_false: tuple[Any, Any] | None = None

    def __call__(
        self,
        value: bool | None = None,
        **kwargs: Any,
    ) -> Self:
        if self.use_true_false is not None:
            value = self.use_true_false[0] if value else self.use_true_false[1]
        return super().__call__(value, **kwargs)

    def __str__(self) -> str:
        if self.use_true_false is not None:
            value = self.use_true_false[0] if self.value else self.use_true_false[1]
            return f'{self.name}="{value}"'
        if self.value:
            return self.name
        return ""


class ComposePolicy(BaseModel):
    """Defines how multiple values are composed together."""

    composer: Callable[[Iterable[str]], str]
    decomposer: Callable[[str], Iterable[str]]
    kwarg_composer: Callable[[str, str], str] | None = None
    remove_duplicates: bool = True


class ComposedAttribute(SimpleAttribute, frozen=True):
    """Allows multiple values to be composed together."""

    policy: ComposePolicy
    composed_values: tuple[str, ...] | None = None

    def _decompose_values(self, values: list[str]) -> list[str]:
        decomposed_values: list[str] = []
        for val in values:
            decomposed_values.extend(self.policy.decomposer(val))
        return decomposed_values

    def __call__(
        self,
        value: str | dict[str, Any] | None = None,
        *values: str | None,
        add_after: bool = True,
        clean_underscores: bool = True,
        **kwargs: str,
    ) -> Self:
        """The flag add_after determines whether to include kwargs before or after values."""
        if kwargs and not self.policy.kwarg_composer:
            raise ValueError(
                "kwarg_composer must be provided to use keyword arguments."
            )
        kwargs = _clean_kwargs(kwargs, underscores_to_hyphens=clean_underscores)
        # The items in value of type dict are not being cleaned.
        if isinstance(value, dict):
            if kwargs:
                value.update(kwargs)
            kwargs = value
        else:
            values = (value, *values)

        decomposed = self._decompose_values([val for val in values if val is not None])
        values = tuple(dict.fromkeys(decomposed, None).keys())

        kwarg_values: tuple[str, ...] = (
            tuple(self.policy.kwarg_composer(key, val) for key, val in kwargs.items())
            if self.policy.kwarg_composer
            else ()
        )

        joined_values = values + kwarg_values if add_after else kwarg_values + values
        composed_values = tuple(value for value in joined_values if value is not None)
        return super().__call__(
            self.policy.composer(composed_values),
            composed_values=composed_values,
        )

    def merge(self, other: Attribute) -> ComposedAttribute:
        if not isinstance(other, ComposedAttribute):
            return super().merge(other)
        if self.name != other.name:
            raise ValueError(
                f"Cannot merge attributes with different names: {self.name} and {other.name}"
            )
        self_values: tuple[str, ...] = (
            self.composed_values if self.composed_values else ()
        )
        other_values: tuple[str, ...] = (
            other.composed_values if other.composed_values else ()
        )
        total_values = self_values + other_values
        if self.policy.remove_duplicates:
            # Remove duplicates while preserving order
            total_values = tuple(dict.fromkeys(total_values, None).keys())
        return self.__call__(*total_values)

    def __contains__(self, item: Any) -> bool:
        """Returns True if the item is in the composed values, or if the item is also a 
        ComposedAttribute, whether their composed values are a subset."""
        if isinstance(item, ComposedAttribute):
            if self.composed_values is None or item.composed_values is None:
                return False
            return all(val in self.composed_values for val in item.composed_values)
        elif isinstance(item, SimpleAttribute):
            if self.composed_values is None or item.value is None:
                return False
            return item.name == self.name and item.value in self.composed_values
        if not isinstance(item, str) or self.composed_values is None:
            return False
        return item in self.composed_values


def _convert_to_attributes_dict(
    attr_like: AttributeLike,
) -> OrderedDict[str, Attribute]:
    from tymx.base.config import attribute_string_handler

    def _match_attributes_recursive(
        attribute: AttributeLike, attr_dict: OrderedDict[str, list[Attribute]]
    ) -> None:
        match attribute:
            case None:
                return
            case str():
                str_attr = attribute_string_handler(attribute)
                if attribute in attr_dict:
                    attr_dict[attribute].append(str_attr)
                else:
                    attr_dict[attribute] = [str_attr]
            case Attribute():
                if attribute.name in attr_dict:
                    attr_dict[attribute.name].append(attribute)
                else:
                    attr_dict[attribute.name] = [attribute]
            case Attributes():
                for a in attribute:
                    if a.name in attr_dict:
                        attr_dict[a.name].append(a)
                    else:
                        attr_dict[a.name] = [a]
            case Sequence():
                for item in attribute:
                    _match_attributes_recursive(item, attr_dict)
            case _:
                raise ValueError(f"Invalid attribute type: {type(attribute)}.")

    attr_dict: OrderedDict[str, list[Attribute]] = OrderedDict()
    _match_attributes_recursive(attr_like, attr_dict)
    return OrderedDict(
        (name, attr_list[0].merge_all(attr_list[1:]))
        for name, attr_list in attr_dict.items()
    )


class Attributes(BaseModifier, frozen=False):  # type: ignore
    consumer_policy = ConsumerPolicy.DIRECT_BUILT_CHILDREN

    _attributes: OrderedDict[str, Attribute] = field(
        alias="attributes",
        converter=_convert_to_attributes_dict,
        kw_only=False,
        default=None,
    )

    def keys(self) -> KeysView[str]:
        return self._attributes.keys()
    
    def values(self) -> ValuesView[Attribute]:
        return self._attributes.values()

    def items(self) -> dict[str, Any]:
        return {attr.name: attr.value for attr in self._attributes.values()}

    def add(self, attribute: Attribute, overwrite: bool = True) -> None:
        if attribute.name not in self.keys():
            self._attributes[attribute.name] = attribute
        elif overwrite:
            self._attributes[attribute.name] = (
                self._attributes[attribute.name] | attribute
            )
        else:
            self._attributes[attribute.name] = (
                attribute | self._attributes[attribute.name]
            )

    def update(self, attributes: AttributeLike, overwrite: bool = True) -> None:
        attr_dict = _convert_to_attributes_dict(attributes)
        for attr in attr_dict.values():
            self.add(attr, overwrite=overwrite)

    def copy(self) -> Self:
        return evolve(self, attributes=self._attributes.values())

    @override
    def merge(self, other: Consumable | AttributeLike) -> Self:
        """Merges with other by overwriting with other's attributes."""
        return evolve(self, attributes=[self, other])
    
    @override
    def post_init(self, component: Component) -> None:
        pass

    @override
    def apply(self, context: Context) -> None:
        attributes = context.data.attributes
        if attributes is not None:
            attributes.update(self)

    @override
    def transform(self, result: list[Component]) -> list[Component]:
        return result

    def __call__(self) -> Self:
        return self

    def __len__(self) -> int:
        return len(self._attributes)

    def __iter__(self) -> Iterator[Attribute]:
        return iter(self._attributes.values())

    def __contains__(self, attr: Attribute) -> bool:
        return attr.name in self._attributes and attr in self._attributes[attr.name]

    def __str__(self) -> str:
        return " ".join(str(attr) for attr in self._attributes.values())

    def __bool__(self) -> bool:
        return bool(self._attributes)

    def __or__(self, other: Attributes) -> Self:
        return self.merge(other)

    def __ior__(self, other: Attributes) -> Self:
        self.update(other)
        return self

    def __getitem__(self, key: str) -> Attribute:
        return self._attributes[key]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Attributes):
            # compare regardless of order
            return dict(self._attributes) == dict(other._attributes)
        if isinstance(other, Attribute):
            return (
                len(self) == 1
                and other.name in self._attributes
                and other == self._attributes[other.name]
            )
        return NotImplemented


class FrozenAttributes(Attributes, frozen=True):  # type: ignore
    @override
    def add(self, attribute: Attribute, overwrite: bool = True) -> None:
        raise TypeError("FrozenAttributes cannot be modified.")

    @override
    def update(self, attributes: AttributeLike, overwrite: bool = True) -> None:
        raise TypeError("FrozenAttributes cannot be modified.")
