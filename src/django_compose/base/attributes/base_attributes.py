from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Callable, Iterable, Self


def _add_init_kwargs(
    init_kwargs: dict[str, Any] | None, **kwargs: Any
) -> dict[str, Any]:
    if init_kwargs is None:
        init_kwargs = dict()
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


class Attribute(ABC):
    """A modifier which adds attributes to a Component.

    A Attribute can hold multiple attribute values, which can be set when the Attribute is called.
    The default value for each attribute is an empty string.
    """

    def __init__(self, name: str, *, value: Any | None = None) -> None:
        self.name = name
        self.value = value

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
                **(init_kwargs if init_kwargs else dict()),
            )
        except TypeError as e:
            raise TypeError(
                str(e)
                + "\n- likely due to subclass not passing all required arguments for __init__ in its __call__ method."
            )

    def __ior__(self, other: Self) -> None:
        return self.merge(other)

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()

    def merge(self, other: "Attribute") -> None:
        """Default behavior is to override own value with the other attribute's value."""
        self.value = other.value


class SimpleAttribute(Attribute):

    def __init__(self, name: str, *, value: str | None = None) -> None:
        super().__init__(name, value=value)

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

    def __init__(
        self,
        name: str,
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


class ComposePolicy:
    """Defines how multiple values are composed together."""

    def __init__(
        self,
        composer: Callable[[Iterable[str]], str],
        kwarg_composer: Callable[[str, str], str] | None = None,
        remove_duplicates: bool | None = None,
    ) -> None:
        """If remove_duplicates is None, it defaults to False if kwarg_composer is provided."""
        if remove_duplicates is None:
            remove_duplicates = kwarg_composer is None
        self.composer = composer
        self.kwarg_composer = kwarg_composer
        self.remove_duplicates = remove_duplicates


class ComposedAttribute(SimpleAttribute):
    """Allows multiple values to be composed together."""

    def __init__(
        self,
        name: str,
        *,
        # do not forget to register these kwargs in __call__ under _add_init_kwargs
        compose_policy: ComposePolicy,
        composed_values: tuple[str, ...] | None = None,
        value: str | None = None,
    ) -> None:
        super().__init__(name, value=value)
        self.policy = compose_policy
        self.composed_values = composed_values

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
            values = (value,) + values
        kwarg_values: tuple[str, ...] = (
            tuple(
                self.policy.kwarg_composer(key, value) for key, value in kwargs.items()
            )
            if self.policy.kwarg_composer
            else tuple()
        )
        joined_values = values + kwarg_values if add_after else kwarg_values + values
        composed_values = tuple(value for value in joined_values if value is not None)
        return super().__call__(
            self.policy.composer(composed_values),
            init_kwargs=_add_init_kwargs(
                init_kwargs, composed_values=composed_values, compose_policy=self.policy
            ),
        )

    def merge(self, other: Attribute) -> None:
        if not isinstance(other, ComposedAttribute):
            super().merge(other)
            return
        self_values: tuple[str, ...] = (
            self.composed_values if self.composed_values else tuple()
        )
        other_values: tuple[str, ...] = (
            other.composed_values if other.composed_values else tuple()
        )
        total_values = self_values + other_values
        if self.policy.remove_duplicates:
            total_values = tuple(OrderedDict.fromkeys(total_values).keys())
        self.value = self.policy.composer(total_values)
