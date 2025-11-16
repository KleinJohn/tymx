from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Callable, Iterable, Self


def _add_init_kwargs(init_kwargs: dict[str, Any] | None, **kwargs) -> dict[str, Any]:
    if init_kwargs is None:
        init_kwargs = dict()
    init_kwargs.update(kwargs)
    return init_kwargs


def _clean_kwargs(
    kwarg_dict: dict[str, str], underscores_to_hyphens: bool = True
) -> OrderedDict[str, str]:
    cleaned_kwargs = OrderedDict()
    for key, value in kwarg_dict.items():
        clean_key = key
        clean_value = value
        if underscores_to_hyphens:
            clean_key = clean_key.replace("_", "-")
        cleaned_kwargs[clean_key] = clean_value
    return cleaned_kwargs


class Modifier(ABC):

    @abstractmethod
    def __call__(self) -> Self:
        pass


class Tag(Modifier):
    """A modifier which adds tags to a Component.

    A Tag can hold multiple tag values, which can be set when the Tag is called.
    The default value for each tag is an empty string.
    """

    def __init__(self, *tags: str, values: Iterable[str] | None = None) -> None:
        super().__init__()
        if not values:
            self._values = OrderedDict((tag, "") for tag in tags)
        else:
            self._values = OrderedDict((tag, value) for tag, value in zip(tags, values))

    def __call__(
        self,
        *values: str | None,
        init_kwargs: dict[str, Any] | None = None,
    ) -> Self:
        """Assigns values to the tags.

        The values are assigned to the tags in the order they were defined.
        Leave a value as None to keep the current value for that tag.
        If fewer values are provided than tags, the remaining tags keep their current values.
        """
        len_difference = len(self._values) - len(values)
        if len_difference < 0:
            raise ValueError("Too many values provided for tags.")
        rest = tuple(self._values.values())[-len_difference:]
        try:
            return self.__class__(
                *self.tags,
                values=tuple(
                    value if value is not None else self._values[tag]
                    for tag, value in zip(self.tags, values)
                )
                + rest,
                **(init_kwargs if init_kwargs else dict()),
            )
        except TypeError as e:
            raise TypeError(
                str(e)
                + "\n- likely due to subclass not passing all required arguments for __init__ in its __call__ method."
            )

    def __str__(self) -> str:
        return ", ".join(f'{tag}="{value}"' for tag, value in self._values.items())

    def __or__(self, other: "Tag") -> "Tag":
        dict_union = self.values | other.values
        return Tag(*dict_union.keys(), values=dict_union.values())

    def __ror__(self, other: "Tag") -> "Tag":
        return self.__or__(other)

    @property
    def tags(self) -> Iterable[str]:
        return self._values.keys()

    @property
    def values(self) -> OrderedDict[str, str]:
        return self._values


class SingleTag(Tag):
    """Adds a single tag to a Component."""

    def __init__(self, tag: str, *, values: Iterable[str] | None = None) -> None:
        super().__init__(tag, values=values)

    def __call__(
        self,
        *values: str | None,
        init_kwargs: dict[str, Any] | None = None,
    ) -> Self:
        if len(values) > 1:
            raise ValueError(f"{self.tag} only accepts a single value.")
        return super().__call__(*values, init_kwargs=init_kwargs)

    @property
    def tag(self) -> str:
        return next(iter(self._values.keys()))

    @property
    def value(self) -> str:
        return next(iter(self._values.values()))


class ComposedTag(SingleTag):
    """A modifier which adds a single tag to a Component, allowing multiple values to be composed together."""

    def __init__(
        self,
        tag: str,
        /,
        # do not forget to register these kwargs in __call__ under _add_init_kwargs
        composer: Callable[[Iterable[str]], str],
        kwarg_composer: Callable[[str, str], str] | None = None,
        *,
        values: Iterable[str] | None = None,
    ) -> None:
        self.composer = composer
        self.kwarg_composer = kwarg_composer
        super().__init__(tag, values=values)

    def __call__(
        self,
        value: str | dict[str, str] | None = None,
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
