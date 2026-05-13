from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import Any, ClassVar, Literal, TypeVar, final, override

from attrs import define, field

C = TypeVar("C", bound="ColorMixin")


def color_converter(
    color_cls: type[C],
) -> Callable[[C | str | None], str | None]:
    def converter(value: C | str | None) -> str | None:
        match value:
            case None:
                return None
            case _ColorBuilder():
                return value
            case ColorBase():
                # Call base to apply validation logic in value property
                return color_cls(value).base.value
            case str():
                return value

    return converter


class ColorMixin:
    def __init__(self, color: str, **kwargs: Any) -> None:
        super().__init__(color, **kwargs)  # type: ignore

    @property
    def value(self) -> str:
        return super().value  # type: ignore

    def copy_with(self, **kwargs: Any) -> _ColorBuilder:
        return _ColorBuilder(color=self.value, **kwargs)

    @property
    def base(self) -> _ColorBuilder:
        """Resets any previous changes and returns a builder for the base color."""
        return _ColorBuilder(color=self.value)

    @property
    def text(self) -> _ColorBuilder:
        return self.copy_with(type="text")

    @property
    def background(self) -> _ColorBuilder:
        return self.copy_with(type="background")

    @property
    def light(self) -> _ColorBuilder:
        return self.copy_with(variation="light")

    @property
    def dark(self) -> _ColorBuilder:
        return self.copy_with(variation="dark")

    @property
    def soft(self) -> _ColorBuilder:
        return self.copy_with(variation="soft")

    @property
    def bold(self) -> _ColorBuilder:
        return self.copy_with(variation="bold")

    @property
    def on_scheme(self) -> _ColorBuilder:
        return self.copy_with(variation="on-scheme")

    def shade(self, value: int) -> _ColorBuilder:
        return self.copy_with(variation=value)

    @property
    def invert(self) -> _ColorBuilder:
        return self.copy_with(invert=True)


class ColorBase(ColorMixin, StrEnum):
    pass


@final
@define(kw_only=True, slots=True, frozen=True)
class _ColorBuilder(ColorMixin, str):
    _color: str = field(alias="color")
    _type: Literal["color", "text", "background"] = field(alias="type", default="color")
    _variation: Literal["light", "dark", "soft", "bold", "on-scheme"] | int | None = field(
        alias="variation", default=None
    )
    _invert: bool = field(alias="invert", default=False)

    def __new__(
        cls,
        color: str,
        type: Literal["color", "text", "background"] = "color",
        variation: (Literal["light", "dark", "soft", "bold", "on-scheme"] | int | None) = None,
        invert: bool = False,
    ):
        prefix = "is-"
        col = color.split(prefix)[-1]
        var = ""
        inv = "-invert" if invert else ""

        if type == "text":
            prefix = "has-text-"
        elif type == "background":
            prefix = "has-background-"
        if variation is not None:
            var = f"-{variation}" if not isinstance(variation, int) else f"-{variation:02d}"

        obj = super().__new__(cls, f"{prefix}{col}{var}{inv}")

        object.__setattr__(obj, "_color", color)
        object.__setattr__(obj, "_type", type)
        object.__setattr__(obj, "_variation", variation)
        object.__setattr__(obj, "_invert", invert)
        obj.validate()
        return obj

    def validate(self) -> None:
        if Color.is_special_color(self._color) and self._type == "color":
            raise ValueError(
                f"Color '{self._color}' can only be used as text or background color. "
                "Consider appending '.text' or '.background' to the color."
            )
        if not Color.is_primary_color(self._color) and self._variation is not None:
            raise ValueError(
                f"Color '{self._color}' does not support variations. "
                "Only primary colors can have variations like '-light' or '-dark'."
            )
        if isinstance(self._variation, int) and (
            not (0 <= self._variation <= 100) or self._variation % 5 != 0
        ):
            raise ValueError("Shade must be a multiple of 5 between 0 and 100.")

    @property
    def value(self) -> str:
        return self

    @override
    def copy_with(self, **kwargs):
        return _ColorBuilder(
            **(
                {
                    "color": self._color,
                    "type": self._type,
                    "variation": self._variation,
                }
                | kwargs
            )
        )

    @override
    def __str__(self) -> str:
        return self.value


class Color(ColorBase):
    # PRIMARY COLORS:
    PRIMARY = "is-primary"
    LINK = "is-link"
    INFO = "is-info"
    SUCCESS = "is-success"
    WARNING = "is-warning"
    DANGER = "is-danger"
    # GREY SHADES:
    WHITE = "is-white"
    BLACK = "is-black"
    LIGHT = "is-light"
    DARK = "is-dark"
    BLACK_BIS = "is-black-bis"
    BLACK_TER = "is-black-ter"
    GREY_DARKER = "is-grey-darker"
    GREY_DARK = "is-grey-dark"
    GREY = "is-grey"
    GREY_LIGHT = "is-grey-light"
    GREY_LIGHTER = "is-grey-lighter"
    WHITE_TER = "is-white-ter"
    WHITE_BIS = "is-white-bis"
    # SPECIAL COLORS:
    CURRENT = "is-current"
    INHERIT = "is-inherit"
    TEXT = "is-text"

    primary_colors: ClassVar[set[str]]
    grey_shades: ClassVar[set[str]]
    special_colors: ClassVar[set[str]]

    @classmethod
    def is_special_color(cls, color: str) -> bool:
        return color in cls.special_colors

    @classmethod
    def is_primary_color(cls, color: str) -> bool:
        return color in cls.primary_colors

    @classmethod
    def is_grey_shade(cls, color: str) -> bool:
        return color in cls.grey_shades


Color.primary_colors = {
    Color.PRIMARY,
    Color.LINK,
    Color.INFO,
    Color.SUCCESS,
    Color.WARNING,
    Color.DANGER,
    Color.TEXT,
}

Color.grey_shades = {
    Color.DARK,
    Color.BLACK,
    Color.BLACK_BIS,
    Color.BLACK_TER,
    Color.GREY_DARKER,
    Color.GREY_DARK,
    Color.GREY,
    Color.GREY_LIGHT,
    Color.GREY_LIGHTER,
    Color.WHITE_TER,
    Color.WHITE_BIS,
    Color.WHITE,
    Color.LIGHT,
}

Color.special_colors = {
    Color.INHERIT,
    Color.CURRENT,
}
