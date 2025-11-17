from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Callable, Iterable, Self


def _add_init_kwargs(init_kwargs: dict[str, Any] | None, **kwargs) -> dict[str, Any]:
    if init_kwargs is None:
        init_kwargs = dict()
    init_kwargs.update(kwargs)
    return init_kwargs


def _clean_kwargs(
    kwarg_dict: dict[str, Any], underscores_to_hyphens: bool = True
) -> OrderedDict[str, Any]:
    cleaned_kwargs = OrderedDict()
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
                value=self.value,
                **(init_kwargs if init_kwargs else dict()),
            )
        except TypeError as e:
            raise TypeError(
                str(e)
                + "\n- likely due to subclass not passing all required arguments for __init__ in its __call__ method."
            )


class SimpleAttribute(Attribute):

    def __init__(self, name: str, *, value: str | None = None) -> None:
        super().__init__(name, value=value)

    def __call__(
        self,
        value: str | None = None,
        init_kwargs: dict[str, Any] | None = None,
    ) -> Self:
        return super().__call__(value, init_kwargs=init_kwargs)


class BooleanAttribute(Attribute):
    """A modifier which adds a boolean attribute to a Component.

    The attribute is included when the value is True, and omitted when the value is False.
    """

    def __init__(self, name: str, value: bool | None = None) -> None:
        if value is None:
            value = True
        super().__init__(name, value=value)

    def __call__(
        self,
        value: str | bool | None = None,
        *values: Any | None,
        init_kwargs: dict[str, Any] | None = None,
    ) -> Self:
        if isinstance(value, bool):
            return super().__call__(value, *values, init_kwargs=init_kwargs)
        if isinstance(value, str):
            return super().__call__(
                value.lower() != "false", *values, init_kwargs=init_kwargs
            )
        return super().__call__(True, *values, init_kwargs=init_kwargs)


class ComposedAttribute(SimpleAttribute):
    """Allows multiple values to be composed together."""

    def __init__(
        self,
        attribute: str,
        /,
        # do not forget to register these kwargs in __call__ under _add_init_kwargs
        composer: Callable[[Iterable[str]], str],
        kwarg_composer: Callable[[str, str], str] | None = None,
        *,
        values: Iterable[str] | None = None,
    ) -> None:
        self.composer = composer
        self.kwarg_composer = kwarg_composer
        super().__init__(attribute, values=values)

    def __call__(
        self,
        value: str | dict[str, Any] | None = None,
        *values: str | None,
        init_kwargs: dict[str, Any] | None = None,
        add_after=True,
        clean_underscores=True,
        **kwargs: str,
    ) -> Self:
        """The flag add_after determines whether to include kwargs before or after values."""
        if kwargs and not self.kwarg_composer:
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
            tuple(self.kwarg_composer(key, value) for key, value in kwargs.items())
            if self.kwarg_composer
            else tuple()
        )
        joined_values = values + kwarg_values if add_after else kwarg_values + values
        return super().__call__(
            self.composer(value for value in joined_values if value is not None),
            init_kwargs=_add_init_kwargs(
                init_kwargs,
                composer=self.composer,
                kwarg_composer=self.kwarg_composer,
            ),
        )
