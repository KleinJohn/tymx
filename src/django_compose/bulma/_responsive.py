from __future__ import annotations
from enum import StrEnum
from typing import ClassVar, Literal, Self, override

from attrs import asdict, define, field

_none_filter = lambda attr, value: value is not None

type _DisplayLiteral = Literal[
    "block", "flex", "inline", "inline-block", "inline-flex", "table"
]


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


@define(kw_only=True, slots=True, frozen=True)
class ResponsiveDisplaySizes:
    mobile: _DisplayLiteral | None = None
    touch: _DisplayLiteral | None = None
    tablet_only: _DisplayLiteral | None = None
    tablet: _DisplayLiteral | None = None
    desktop_only: _DisplayLiteral | None = None
    desktop: _DisplayLiteral | None = None
    widescreen_only: _DisplayLiteral | None = None
    widescreen: _DisplayLiteral | None = None
    fullhd: _DisplayLiteral | None = None


@define(kw_only=True, slots=True, frozen=True)
class ResponsiveHiddenSizes:
    mobile: bool = False
    touch: bool = False
    tablet_only: bool = False
    tablet: bool = False
    desktop_only: bool = False
    desktop: bool = False
    widescreen_only: bool = False
    widescreen: bool = False
    fullhd: bool = False


@define(kw_only=True, slots=True, frozen=True)
class _DisplayBuilder(str):
    BLOCK: ClassVar[_DisplayLiteral] = "block"
    FLEX: ClassVar[_DisplayLiteral] = "flex"
    INLINE: ClassVar[_DisplayLiteral] = "inline"
    INLINE_BLOCK: ClassVar[_DisplayLiteral] = "inline-block"
    INLINE_FLEX: ClassVar[_DisplayLiteral] = "inline-flex"
    TABLE: ClassVar[_DisplayLiteral] = "table"

    _display: _DisplayLiteral | None = field(alias="display", default=None)
    _responsive_displays: ResponsiveDisplaySizes = field(
        alias="responsive_displays", default=ResponsiveDisplaySizes()
    )
    _hidden: bool = field(alias="hidden", default=False)
    _responsive_hidden: ResponsiveHiddenSizes = field(
        alias="responsive_hidden", default=ResponsiveHiddenSizes()
    )
    _invisible: bool = field(alias="invisible", default=False)
    _sr_only: bool = field(alias="sr_only", default=False)

    @override
    def __new__(
        cls,
        display: _DisplayLiteral | None = None,
        responsive_displays: ResponsiveDisplaySizes | None = None,
        hidden: bool | None = None,
        responsive_hidden: ResponsiveHiddenSizes | None = None,
        invisible: bool | None = None,
        sr_only: bool | None = None,
        **kwargs,
    ):
        obj = super().__new__(
            cls,
            cls.from_values(
                display=display,
                responsive_displays=responsive_displays or ResponsiveDisplaySizes(),
                hidden=hidden,
                responsive_hidden=responsive_hidden or ResponsiveHiddenSizes(),
                invisible=invisible,
                sr_only=sr_only,
            ),
            **kwargs,
        )
        return obj

    @classmethod
    def from_values(
        cls,
        *,
        display: _DisplayLiteral | None = None,
        responsive_displays: ResponsiveDisplaySizes,
        hidden: bool | None = None,
        responsive_hidden: ResponsiveHiddenSizes,
        invisible: bool | None = None,
        sr_only: bool | None = None,
    ) -> str:
        classes: list[str] = []

        if display is not None:
            classes.append(f"is-{display}")
        for size, value in asdict(responsive_displays, filter=_none_filter).items():
            classes.append(f"is-{value}-{size.replace('_', '-')}")

        if hidden:
            classes.append("is-hidden")
        for size, active in asdict(responsive_hidden, filter=lambda k, v: v).items():
            classes.append(f"is-hidden-{size.replace('_', '-')}")

        if invisible:
            classes.append("is-invisible")
        if sr_only:
            classes.append("is-sr-only")

        return " ".join(classes)

    def with_values(
        self,
        *,
        display: _DisplayLiteral | None = None,
        responsive_displays: ResponsiveDisplaySizes | None = None,
        hidden: bool | None = None,
        responsive_hidden: ResponsiveHiddenSizes | None = None,
        invisible: bool | None = None,
        sr_only: bool | None = None,
    ) -> Self:
        return self.__class__(
            display=self._display if display is None else display,
            responsive_displays=responsive_displays or self._responsive_displays,
            hidden=self._hidden if hidden is None else hidden,
            responsive_hidden=responsive_hidden or self._responsive_hidden,
            invisible=self._invisible if invisible is None else invisible,
            sr_only=self._sr_only if sr_only is None else sr_only,
        )

    def display(
        self,
        display: _DisplayLiteral | None = None,
        *,
        mobile: _DisplayLiteral | None = None,
        touch: _DisplayLiteral | None = None,
        tablet_only: _DisplayLiteral | None = None,
        tablet: _DisplayLiteral | None = None,
        desktop_only: _DisplayLiteral | None = None,
        desktop: _DisplayLiteral | None = None,
        widescreen_only: _DisplayLiteral | None = None,
        widescreen: _DisplayLiteral | None = None,
        fullhd: _DisplayLiteral | None = None,
    ) -> Self:
        return self.with_values(
            display=display,
            responsive_displays=ResponsiveDisplaySizes(
                mobile=mobile or self._responsive_displays.mobile,
                touch=touch or self._responsive_displays.touch,
                tablet_only=tablet_only or self._responsive_displays.tablet_only,
                tablet=tablet or self._responsive_displays.tablet,
                desktop_only=desktop_only or self._responsive_displays.desktop_only,
                desktop=desktop or self._responsive_displays.desktop,
                widescreen_only=widescreen_only
                or self._responsive_displays.widescreen_only,
                widescreen=widescreen or self._responsive_displays.widescreen,
                fullhd=fullhd or self._responsive_displays.fullhd,
            ),
        )

    def hide(
        self,
        hidden: bool | None = None,
        *,
        mobile: bool = False,
        touch: bool = False,
        tablet_only: bool = False,
        tablet: bool = False,
        desktop_only: bool = False,
        desktop: bool = False,
        widescreen_only: bool = False,
        widescreen: bool = False,
        fullhd: bool = False,
    ) -> Self:
        return self.with_values(
            hidden=hidden,
            responsive_hidden=ResponsiveHiddenSizes(
                mobile=mobile or self._responsive_hidden.mobile,
                touch=touch or self._responsive_hidden.touch,
                tablet_only=tablet_only or self._responsive_hidden.tablet_only,
                tablet=tablet or self._responsive_hidden.tablet,
                desktop_only=desktop_only or self._responsive_hidden.desktop_only,
                desktop=desktop or self._responsive_hidden.desktop,
                widescreen_only=widescreen_only
                or self._responsive_hidden.widescreen_only,
                widescreen=widescreen or self._responsive_hidden.widescreen,
                fullhd=fullhd or self._responsive_hidden.fullhd,
            ),
        )

    @property
    def block(self) -> Self:
        return self.with_values(display=self.BLOCK)

    @property
    def flex(self) -> Self:
        return self.with_values(display=self.FLEX)

    @property
    def inline(self) -> Self:
        return self.with_values(display=self.INLINE)

    @property
    def inline_block(self) -> Self:
        return self.with_values(display=self.INLINE_BLOCK)

    @property
    def inline_flex(self) -> Self:
        return self.with_values(display=self.INLINE_FLEX)

    @property
    def table(self) -> Self:
        return self.with_values(display=self.TABLE)

    @property
    def hidden(self) -> Self:
        return self.with_values(hidden=True)

    @property
    def invisible(self) -> Self:
        return self.with_values(invisible=True)

    @property
    def sr_only(self) -> Self:
        return self.with_values(sr_only=True)


Display = _DisplayBuilder()
