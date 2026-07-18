from collections.abc import Callable
from enum import StrEnum
from typing import Literal, TypeVar, overload

from tymx.base.types import StringLike

_E = TypeVar("_E", bound=StrEnum)
_T = TypeVar("_T")


def enum_converter(enum_class: type[_E]) -> Callable[[_E | str], _E]:
    def converter(value: _E | str) -> _E:
        return enum_class(value)

    return converter


def optional_enum_converter(
    enum_class: type[_E],
) -> Callable[[_E | str | None], _E | None]:
    def converter(value: _E | str | None) -> _E | None:
        return enum_class(value) if value is not None else None

    return converter


def string_like_converter(value: StringLike) -> str:
    return str(value)


def optional_string_like_converter(value: StringLike | None) -> str | None:
    return str(value) if value is not None else None


@overload
def string_type_converter(
    or_type: type[_T],
    /,
    optional: Literal[False] = False,
) -> Callable[[_T | str], str]: ...


@overload
def string_type_converter(
    or_type: type[_T],
    /,
    optional: Literal[True],
) -> Callable[[_T | str | None], str | None]: ...


def string_type_converter(
    or_type: type[_T],
    /,
    optional: bool = False,
) -> Callable[[_T | str | None], str | None] | Callable[[_T | str], str]:
    def converter(value: _T | str | None) -> str | None:
        if value is None:
            if not optional:
                raise ValueError(f"{or_type.__name__} field is not optional")
            return None
        return str(value)

    return converter
