from collections.abc import Callable
from enum import StrEnum
from typing import TypeVar

from tymx.base.types import StringLike

E = TypeVar("E", bound=StrEnum)


def enum_converter(enum_class: type[E]) -> Callable[[E | str], E]:
    def converter(value: E | str) -> E:
        return enum_class(value)

    return converter


def optional_enum_converter(
    enum_class: type[E],
) -> Callable[[E | str | None], E | None]:
    def converter(value: E | str | None) -> E | None:
        return enum_class(value) if value is not None else None

    return converter


def string_like_converter(value: StringLike) -> str:
    return str(value)


def optional_string_like_converter(value: StringLike | None) -> str | None:
    return str(value) if value is not None else None
