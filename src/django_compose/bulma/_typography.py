from __future__ import annotations
from enum import StrEnum
from typing import Literal, Self, override

from attrs import define, field, asdict

type _SizeLiteral = Literal[1, 2, 3, 4, 5, 6, 7]


_none_filter = lambda attr, x: x is not None


def _validate_size(
    instance: _TypographyBuilder, attribute: str, value: _SizeLiteral | None
) -> None:
    if value is not None and value not in (1, 2, 3, 4, 5, 6, 7):
        raise ValueError("size must be an integer between 1 and 7.")


def _validate_alignment(
    instance: _TypographyBuilder, attribute: str, value: TextAlignment | None
) -> None:
    if value is not None and value not in TextAlignment:
        raise ValueError("alignment must be a valid TextAlignment.")


class TextAlignment(StrEnum):
    LEFT = "left"
    CENTERED = "centered"
    RIGHT = "right"
    JUSTIFIED = "justified"


class ResponsiveTextAlignment(StrEnum):
    MOBILE = "mobile"
    TOUCH = "touch"
    TABLET_ONLY = "tablet-only"
    TABLET = "tablet"
    DESKTOP_ONLY = "desktop-only"
    DESKTOP = "desktop"
    WIDESCREEN_ONLY = "widescreen-only"
    WIDESCREEN = "widescreen"
    FULLHD = "fullhd"


class TextTransformation(StrEnum):
    CAPITALIZED = "capitalized"
    LOWERCASE = "lowercase"
    UPPERCASE = "uppercase"
    ITALIC = "italic"
    UNDERLINED = "underlined"


class TextWeight(StrEnum):
    LIGHT = "light"
    NORMAL = "normal"
    MEDIUM = "medium"
    SEMIBOLD = "semibold"
    BOLD = "bold"
    EXTRABOLD = "extrabold"


class FontFamily(StrEnum):
    SANS_SERIF = "sans-serif"
    MONOSPACE = "monospace"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    CODE = "code"


@define(kw_only=True, slots=True, frozen=True)
class _ResponsiveTextSize:
    mobile: _SizeLiteral | None = field(default=None, validator=_validate_size)
    touch: _SizeLiteral | None = field(default=None, validator=_validate_size)
    tablet: _SizeLiteral | None = field(default=None, validator=_validate_size)
    desktop: _SizeLiteral | None = field(default=None, validator=_validate_size)
    widescreen: _SizeLiteral | None = field(default=None, validator=_validate_size)
    fullhd: _SizeLiteral | None = field(default=None, validator=_validate_size)


@define(kw_only=True, slots=True, frozen=True)
class _ResponsiveTextAlignment:
    mobile: TextAlignment | None = field(default=None, validator=_validate_alignment)
    touch: TextAlignment | None = field(default=None, validator=_validate_alignment)
    tablet: TextAlignment | None = field(default=None, validator=_validate_alignment)
    desktop: TextAlignment | None = field(default=None, validator=_validate_alignment)
    widescreen: TextAlignment | None = field(
        default=None, validator=_validate_alignment
    )
    fullhd: TextAlignment | None = field(default=None, validator=_validate_alignment)
    tablet_only: TextAlignment | None = field(
        default=None, validator=_validate_alignment
    )
    desktop_only: TextAlignment | None = field(
        default=None, validator=_validate_alignment
    )
    widescreen_only: TextAlignment | None = field(
        default=None, validator=_validate_alignment
    )


@define(kw_only=True, slots=True, frozen=True)
class _TypographyBuilder(str):

    _size: _SizeLiteral | None = field(default=None, alias="size")
    _responsive_sizes: _ResponsiveTextSize | None = field(
        factory=_ResponsiveTextSize, alias="responsive_sizes"
    )
    _alignment: TextAlignment | None = field(default=None, alias="alignment")
    _responsive_alignments: _ResponsiveTextAlignment | None = field(
        factory=_ResponsiveTextAlignment, alias="responsive_alignments"
    )
    _transformation: TextTransformation | None = field(
        default=None, alias="transformation"
    )
    _weight: TextWeight | None = field(default=None, alias="weight")
    _font_family: FontFamily | None = field(default=None, alias="font_family")

    def __new__(
        cls,
        size: _SizeLiteral | None = None,
        responsive_sizes: _ResponsiveTextSize | None = None,
        alignment: TextAlignment | None = None,
        responsive_alignments: _ResponsiveTextAlignment | None = None,
        transformation: TextTransformation | None = None,
        weight: TextWeight | None = None,
        font_family: FontFamily | None = None,
        **kwargs,
    ):
        obj = super().__new__(
            cls,
            cls.from_values(
                size=size,
                responsive_sizes=responsive_sizes or _ResponsiveTextSize(),
                alignment=alignment,
                responsive_alignments=responsive_alignments
                or _ResponsiveTextAlignment(),
                transformation=transformation,
                weight=weight,
                font_family=font_family,
            ),
            **kwargs,
        )
        return obj

    @classmethod
    def from_values(
        cls,
        *,
        size: _SizeLiteral | None = None,
        responsive_sizes: _ResponsiveTextSize,
        alignment: TextAlignment | None = None,
        responsive_alignments: _ResponsiveTextAlignment,
        transformation: TextTransformation | None = None,
        weight: TextWeight | None = None,
        font_family: FontFamily | None = None,
    ) -> str:
        classes = []
        if size is not None:
            classes.append(f"is-size-{size}")
        for s, resp in asdict(responsive_sizes, filter=_none_filter).items():
            classes.append(f"is-size-{s}-{resp}")
        if alignment is not None:
            classes.append(f"has-text-{alignment.value}")
        for al, resp in asdict(responsive_alignments, filter=_none_filter).items():
            classes.append(f"has-text-{al}-{resp}")
        if transformation is not None:
            classes.append(f"is-{transformation.value}")
        if weight is not None:
            classes.append(f"has-text-weight-{weight.value}")
        if font_family is not None:
            classes.append(f"is-family-{font_family.value}")
        return " ".join(classes)

    def with_values(
        self,
        *,
        size: _SizeLiteral | None = None,
        responsive_sizes: _ResponsiveTextSize | None = None,
        alignment: TextAlignment | None = None,
        responsive_alignments: _ResponsiveTextAlignment | None = None,
        transformation: TextTransformation | None = None,
        weight: TextWeight | None = None,
        font_family: FontFamily | None = None,
    ) -> Self:

        if size is not None and size not in (1, 2, 3, 4, 5, 6, 7):
            raise ValueError("size must be an integer between 1 and 7.")

        return self.__class__(
            size=size or self._size,
            responsive_sizes=responsive_sizes or self._responsive_sizes,
            alignment=alignment or self._alignment,
            responsive_alignments=responsive_alignments or self._responsive_alignments,
            transformation=transformation or self._transformation,
            weight=weight or self._weight,
            font_family=font_family or self._font_family,
        )

    def size(
        self,
        size: _SizeLiteral | None = None,
        *,
        mobile: _SizeLiteral | None = None,
        touch: _SizeLiteral | None = None,
        tablet: _SizeLiteral | None = None,
        desktop: _SizeLiteral | None = None,
        widescreen: _SizeLiteral | None = None,
        fullhd: _SizeLiteral | None = None,
    ) -> Self:
        return self.with_values(
            size=size,
            responsive_sizes=_ResponsiveTextSize(
                mobile=mobile or self._responsive_sizes.mobile,
                touch=touch or self._responsive_sizes.touch,
                tablet=tablet or self._responsive_sizes.tablet,
                desktop=desktop or self._responsive_sizes.desktop,
                widescreen=widescreen or self._responsive_sizes.widescreen,
                fullhd=fullhd or self._responsive_sizes.fullhd,
            ),
        )

    def align(
        self,
        alignment: TextAlignment | None = None,
        *,
        mobile: TextAlignment | None = None,
        touch: TextAlignment | None = None,
        tablet: TextAlignment | None = None,
        desktop: TextAlignment | None = None,
        widescreen: TextAlignment | None = None,
        fullhd: TextAlignment | None = None,
        tablet_only: TextAlignment | None = None,
        desktop_only: TextAlignment | None = None,
        widescreen_only: TextAlignment | None = None,
    ) -> Self:
        return self.with_values(
            alignment=alignment,
            responsive_alignments=_ResponsiveTextAlignment(
                mobile=mobile or self._responsive_alignments.mobile,
                touch=touch or self._responsive_alignments.touch,
                tablet=tablet or self._responsive_alignments.tablet,
                desktop=desktop or self._responsive_alignments.desktop,
                widescreen=widescreen or self._responsive_alignments.widescreen,
                fullhd=fullhd or self._responsive_alignments.fullhd,
                tablet_only=tablet_only or self._responsive_alignments.tablet_only,
                desktop_only=desktop_only or self._responsive_alignments.desktop_only,
                widescreen_only=widescreen_only
                or self._responsive_alignments.widescreen_only,
            ),
        )

    # Alignment shortcuts
    @property
    def left(self) -> Self:
        return self.with_values(alignment=TextAlignment.LEFT)

    @property
    def centered(self) -> Self:
        return self.with_values(alignment=TextAlignment.CENTERED)

    @property
    def right(self) -> Self:
        return self.with_values(alignment=TextAlignment.RIGHT)

    @property
    def justified(self) -> Self:
        return self.with_values(alignment=TextAlignment.JUSTIFIED)

    # Text transformation shortcuts
    @property
    def capitalized(self) -> Self:
        return self.with_values(transformation=TextTransformation.CAPITALIZED)

    @property
    def lowercase(self) -> Self:
        return self.with_values(transformation=TextTransformation.LOWERCASE)

    @property
    def uppercase(self) -> Self:
        return self.with_values(transformation=TextTransformation.UPPERCASE)

    @property
    def italic(self) -> Self:
        return self.with_values(transformation=TextTransformation.ITALIC)

    @property
    def underlined(self) -> Self:
        return self.with_values(transformation=TextTransformation.UNDERLINED)

    # Text weight shortcuts
    @property
    def light(self) -> Self:
        return self.with_values(weight=TextWeight.LIGHT)

    @property
    def normal(self) -> Self:
        return self.with_values(weight=TextWeight.NORMAL)

    @property
    def medium(self) -> Self:
        return self.with_values(weight=TextWeight.MEDIUM)

    @property
    def semibold(self) -> Self:
        return self.with_values(weight=TextWeight.SEMIBOLD)

    @property
    def bold(self) -> Self:
        return self.with_values(weight=TextWeight.BOLD)

    @property
    def extrabold(self) -> Self:
        return self.with_values(weight=TextWeight.EXTRABOLD)

    # Font family shortcuts
    @property
    def sans_serif(self) -> Self:
        return self.with_values(font_family=FontFamily.SANS_SERIF)

    @property
    def monospace(self) -> Self:
        return self.with_values(font_family=FontFamily.MONOSPACE)

    @property
    def family_primary(self) -> Self:
        return self.with_values(font_family=FontFamily.PRIMARY)

    @property
    def family_secondary(self) -> Self:
        return self.with_values(font_family=FontFamily.SECONDARY)

    @property
    def family_code(self) -> Self:
        return self.with_values(font_family=FontFamily.CODE)

    @override
    @property
    def center(self) -> Self:
        return self.centered


Text = _TypographyBuilder()
