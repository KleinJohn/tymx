from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Callable, Iterable, Sequence
from typing import cast

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, SkipValidation
from typing_extensions import (
    Annotated,
    Any,
    Self,
    override,
    ClassVar,
    Iterator,
)

from django_compose.base.config import attribute_string_handler
from django_compose.base.context import Consumable, ConsumerPolicy
from django_compose.base.types import AttributeLike


def _add_init_kwargs(
    init_kwargs: dict[str, Any] | None, **kwargs: Any
) -> dict[str, Any]:
    if init_kwargs is None:
        init_kwargs = {}
    init_kwargs.update(kwargs)
    return init_kwargs


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


class Attribute(BaseModel, ABC):
    """A modifier which adds attributes to a Component.

    A Attribute can hold multiple attribute values, which can be set when the Attribute is called.
    The default value for each attribute is an empty string.
    """

    name: str = Field(kw_only=False)
    value: Any | None = None

    def __init__(self, name: str, **data: Any) -> None:
        super().__init__(name=name, **data)

    def __call__(
        self, value: Any | None = None, *, init_kwargs: dict[str, Any] | None = None
    ) -> Self:
        """Assigns values to the attributes.

        The values are assigned to the attributes in the order they were defined.
        Leave a value as None to keep the current value for that attribute.
        If fewer values are provided than attributes, the remaining attributes keep their current values.
        Overrides of this method should call their parent's __call__ method.
        """
        try:
            return self.__class__(
                self.name,
                value=value,
                **(init_kwargs if init_kwargs else {}),
            )
        except TypeError as e:
            raise TypeError(
                str(e)
                + "\n- likely due to subclass not passing all required arguments for __init__ in its __call__ method."
            ) from e

    def __or__(self, other: Self) -> Self:
        return self.merge(other)

    def __contains__(self, item: Any) -> bool:
        return item == self.value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Attribute):
            return NotImplemented
        return self.name == other.name and self.value == other.value

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()

    def merge(self, other: "Attribute") -> Self:
        """Default behavior is to override own value with the other attribute's value."""
        if self.name != other.name:
            raise ValueError(
                f"Cannot merge attributes with different names: {self.name} and {other.name}"
            )
        return self.__class__(self.name, value=other.value)


class SimpleAttribute(Attribute):
    value: str | None = None

    def __call__(
        self,
        value: str | None = None,
        *,
        init_kwargs: dict[str, Any] | None = None,
    ) -> Self:
        return super().__call__(value, init_kwargs=init_kwargs)

    def __str__(self) -> str:
        if self.value is None:
            return ""
        return f'{self.name}="{self.value}"'


class BooleanAttribute(Attribute):
    """A modifier which adds a boolean attribute to a Component.

    The attribute is included when the value is True, and omitted when the value is False.
    """

    value: bool | None = None
    use_true_false: tuple[Any, Any] | None = None

    def __init__(
        self,
        name: str,
        *,
        value: bool | None = None,
        use_true_false: tuple[Any, Any] | None = None,
    ) -> None:
        if value is None:
            value = True
        super().__init__(name, value=value)
        self.use_true_false = use_true_false

    def __call__(
        self,
        value: bool | None = None,
        *,
        init_kwargs: dict[str, Any] | None = None,
    ) -> Self:
        if self.use_true_false is not None:
            value = self.use_true_false[0] if value else self.use_true_false[1]
        return super().__call__(
            value,
            init_kwargs=_add_init_kwargs(
                init_kwargs, use_true_false=self.use_true_false
            ),
        )

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


class ComposedAttribute(SimpleAttribute):
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
        init_kwargs: dict[str, Any] | None = None,
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
            init_kwargs=_add_init_kwargs(
                init_kwargs, composed_values=composed_values, policy=self.policy
            ),
        )

    def merge(self, other: Attribute) -> "ComposedAttribute":
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
        return self(*total_values)

    def __contains__(self, item: Any) -> bool:
        if not isinstance(item, str) or self.composed_values is None:
            return False
        return item in self.composed_values


def _convert_to_attributes_dict(
    attr_like: AttributeLike,
) -> OrderedDict[str, Attribute]:
    def _match_attributes_recursive(
        attribute: AttributeLike, attr_dict: OrderedDict[str, Attribute]
    ) -> None:
        match attribute:
            case None:
                return
            case str():
                attr_dict[attribute] = attribute_string_handler(attribute)
            case Attribute():
                attr_dict[attribute.name] = attribute
            case Attributes():
                for a in attribute:
                    attr_dict[a.name] = a
            case Sequence():
                for item in attribute:
                    _match_attributes_recursive(item, attr_dict)
            case _:
                raise ValueError(f"Invalid attribute type: {type(attribute)}.")

    attr_dict: OrderedDict[str, Attribute] = OrderedDict()
    _match_attributes_recursive(attr_like, attr_dict)
    return attr_dict


class Attributes(Consumable):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.DIRECT_BUILT_CHILDREN

    internal_data: SkipValidation[AttributeLike] = Field(
        alias="attributes",
        init=True,
        default=None,
        kw_only=False,
        exclude=True,
    )

    def __init__(self, *attributes: AttributeLike) -> None:
        super().__init__(attributes=_convert_to_attributes_dict(attributes))  # type: ignore

    @property
    def _data(self) -> OrderedDict[str, Attribute]:
        return cast(OrderedDict[str, Attribute], self.internal_data)

    def values(self) -> dict[str, Any]:
        return {attr.name: attr.value for attr in self._data.values()}

    def add(self, attribute: Attribute, overwrite: bool = True) -> None:
        if attribute.name not in self:
            self._data[attribute.name] = attribute
        elif overwrite:
            self._data[attribute.name] = self._data[attribute.name] | attribute
        else:
            self._data[attribute.name] = attribute | self._data[attribute.name]

    def update(self, attributes: AttributeLike, overwrite: bool = True) -> None:
        attr_dict = _convert_to_attributes_dict(attributes)
        for attr in attr_dict.values():
            self.add(attr, overwrite=overwrite)

    @override
    def merge(self, other: Attributes) -> Self:
        return self.__class__([self, other])

    def copy(self) -> Self:
        return self.__class__(self)

    def __call__(self) -> Self:
        return self

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Attribute]:
        return iter(self._data.values())

    def __contains__(self, item: str | Attribute) -> bool:
        if isinstance(item, str):
            return item in self._data
        return item.name in self._data

    def __str__(self) -> str:
        return " ".join(str(attr) for attr in self._data.values())

    def __bool__(self) -> bool:
        return bool(self._data)

    def __or__(self, other: Attributes) -> Self:
        return self.merge(other)

    def __ior__(self, other: Attributes) -> Self:
        self.update(other)
        return self

    def __getitem__(self, key: str) -> Attribute:
        return self._data[key]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Attributes):
            # compare regardless of order
            return dict(self._data) == dict(other._data)
        if isinstance(other, Attribute):
            return (
                len(self) == 1
                and other.name in self._data
                and other == self._data[other.name]
            )
        return NotImplemented


class FrozenAttributes(Attributes):
    model_config = ConfigDict(frozen=True)

    @override
    def add(self, attribute: Attribute, overwrite: bool = True) -> None:
        raise TypeError("FrozenAttributes cannot be modified.")

    @override
    def update(self, attributes: AttributeLike, overwrite: bool = True) -> None:
        raise TypeError("FrozenAttributes cannot be modified.")


# Resolve forward references for recursive AttributeLike typing.
Attributes.model_rebuild()
FrozenAttributes.model_rebuild()
