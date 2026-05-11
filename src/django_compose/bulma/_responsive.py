from __future__ import annotations
from enum import StrEnum

from attrs import define, field


@define(kw_only=True, slots=True, frozen=True)
class DisplayBuilder(str):

    _display: DisplayValue = field(alias="display", kw_only=False)
    _size: DisplaySize | None = field(alias="size", default=None)


class DisplayValue(StrEnum):
    BLOCK = "is-block"
    FLEX = "is-flex"
    INLINE = "is-inline"
    INLINE_BLOCK = "is-inline-block"
    INLINE_FLEX = "is-inline-flex"
    TABLE = "is-table"


class DisplaySize(StrEnum):
    MOBILE = "mobile"
    TOUCH = "touch"
    TABLET_ONLY = "tablet-only"
    TABLET = "tablet"
    DESKTOP_ONLY = "desktop-only"
    DESKTOP = "desktop"
    WIDESCREEN_ONLY = "widescreen-only"
    WIDESCREEN = "widescreen"
    FULLHD = "fullhd"
