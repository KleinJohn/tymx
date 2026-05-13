from collections.abc import Callable
from enum import StrEnum
from typing import TypeVar

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
