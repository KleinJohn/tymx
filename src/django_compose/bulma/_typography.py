from __future__ import annotations
from enum import StrEnum
from typing import Literal, Self, override

from attrs import define, field


@define(kw_only=True, slots=True, frozen=True)
class TextBuilder(str):

    _size: Literal[1, 2, 3, 4, 5, 6, 7] | None = field(default=None, alias="size")
    _responsive_size: ResponsiveTextSize | None = field(
        default=None, alias="responsive_size"
    )
    _alignment: TextAlignment | None = field(default=None, alias="alignment")
    _responsive_alignment: ResponsiveTextAlignment | None = field(
        default=None, alias="responsive_alignment"
    )
    _transformation: TextTransformation | None = field(
        default=None, alias="transformation"
    )
    _weight: TextWeight | None = field(default=None, alias="weight")
    _font_family: FontFamily | None = field(default=None, alias="font_family")

    def __new__(
        cls,
        size: Literal[1, 2, 3, 4, 5, 6, 7] | None = None,
        responsive_size: ResponsiveTextSize | None = None,
        alignment: TextAlignment | None = None,
        responsive_alignment: ResponsiveTextAlignment | None = None,
        transformation: TextTransformation | None = None,
        weight: TextWeight | None = None,
        font_family: FontFamily | None = None,
        **kwargs,
    ):
        obj = super().__new__(
            cls,
            cls.from_values(
                size=size,
                responsive_size=responsive_size,
                alignment=alignment,
                responsive_alignment=responsive_alignment,
                transformation=transformation,
                weight=weight,
                font_family=font_family,
            ),
            **kwargs,
        )
        return obj

    @classmethod
    def validate_values(
        cls,
        size: Literal[1, 2, 3, 4, 5, 6, 7] | None = None,
        responsive_size: ResponsiveTextSize | None = None,
        alignment: TextAlignment | None = None,
        responsive_alignment: ResponsiveTextAlignment | None = None,
        transformation: TextTransformation | None = None,
        weight: TextWeight | None = None,
        font_family: FontFamily | None = None,
    ) -> None:
        if size is not None and size not in {1, 2, 3, 4, 5, 6, 7}:
            raise ValueError("Size must be between 1 and 7.")
        if size is None and responsive_size is not None:
            raise ValueError("Responsive size cannot be set without a base size.")
        if alignment is None and responsive_alignment is not None:
            raise ValueError(
                "Responsive alignment cannot be set without a base alignment."
            )

    @classmethod
    def from_values(
        cls,
        *,
        size: Literal[1, 2, 3, 4, 5, 6, 7] | None = None,
        responsive_size: ResponsiveTextSize | None = None,
        alignment: TextAlignment | None = None,
        responsive_alignment: ResponsiveTextAlignment | None = None,
        transformation: TextTransformation | None = None,
        weight: TextWeight | None = None,
        font_family: FontFamily | None = None,
    ) -> str:
        cls.validate_values(
            size=size,
            responsive_size=responsive_size,
            alignment=alignment,
            responsive_alignment=responsive_alignment,
            transformation=transformation,
            weight=weight,
            font_family=font_family,
        )
        size_class = None
        alignment_class = None
        if size is not None:
            size_class = f"is-size-{size}"
            if responsive_size is not None:
                size_class = f"{size_class}-{responsive_size.value}"
        if alignment is not None:
            alignment_class = f"has-text-{alignment.value}"
            if responsive_alignment is not None:
                alignment_class = f"{alignment_class}-{responsive_alignment.value}"

        transformation_class = f"is-{transformation.value}" if transformation else None
        weight_class = f"has-text-weight-{weight.value}" if weight else None
        font_family_class = f"is-family-{font_family.value}" if font_family else None

        # Filter out None/empty values before joining
        return " ".join(
            part
            for part in (
                size_class,
                alignment_class,
                transformation_class,
                weight_class,
                font_family_class,
            )
            if part
        )

    def with_values(
        self,
        *,
        size: Literal[1, 2, 3, 4, 5, 6, 7] | None = None,
        responsive_size: ResponsiveTextSize | None = None,
        alignment: TextAlignment | None = None,
        responsive_alignment: ResponsiveTextAlignment | None = None,
        transformation: TextTransformation | None = None,
        weight: TextWeight | None = None,
        font_family: FontFamily | None = None,
    ) -> Self:
        return self.__class__(
            size=size or self._size,
            responsive_size=responsive_size or self._responsive_size,
            alignment=alignment or self._alignment,
            responsive_alignment=responsive_alignment or self._responsive_alignment,
            transformation=transformation or self._transformation,
            weight=weight or self._weight,
            font_family=font_family or self._font_family,
        )

    def size(self, size: Literal[1, 2, 3, 4, 5, 6, 7]) -> Self:
        return self.with_values(size=size)

    @property
    def mobile(self) -> Self:
        return self.with_values(responsive_size=ResponsiveTextSize.MOBILE)

    @property
    def touch(self) -> Self:
        return self.with_values(responsive_size=ResponsiveTextSize.TOUCH)

    @property
    def tablet(self) -> Self:
        return self.with_values(responsive_size=ResponsiveTextSize.TABLET)

    @property
    def desktop(self) -> Self:
        return self.with_values(responsive_size=ResponsiveTextSize.DESKTOP)

    @property
    def widescreen(self) -> Self:
        return self.with_values(responsive_size=ResponsiveTextSize.WIDESCREEN)

    @property
    def fullhd(self) -> Self:
        return self.with_values(responsive_size=ResponsiveTextSize.FULLHD)

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

    # Responsive alignment shortcuts (prefixed to avoid name conflicts with size responsive helpers)
    @property
    def align_mobile(self) -> Self:
        return self.with_values(responsive_alignment=ResponsiveTextAlignment.MOBILE)

    @property
    def align_touch(self) -> Self:
        return self.with_values(responsive_alignment=ResponsiveTextAlignment.TOUCH)

    @property
    def align_tablet_only(self) -> Self:
        return self.with_values(
            responsive_alignment=ResponsiveTextAlignment.TABLET_ONLY
        )

    @property
    def align_tablet(self) -> Self:
        return self.with_values(responsive_alignment=ResponsiveTextAlignment.TABLET)

    @property
    def align_desktop_only(self) -> Self:
        return self.with_values(
            responsive_alignment=ResponsiveTextAlignment.DESKTOP_ONLY
        )

    @property
    def align_desktop(self) -> Self:
        return self.with_values(responsive_alignment=ResponsiveTextAlignment.DESKTOP)

    @property
    def align_widescreen_only(self) -> Self:
        return self.with_values(
            responsive_alignment=ResponsiveTextAlignment.WIDESCREEN_ONLY
        )

    @property
    def align_widescreen(self) -> Self:
        return self.with_values(responsive_alignment=ResponsiveTextAlignment.WIDESCREEN)

    @property
    def align_fullhd(self) -> Self:
        return self.with_values(responsive_alignment=ResponsiveTextAlignment.FULLHD)

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


class ResponsiveTextSize(StrEnum):
    MOBILE = "mobile"
    TOUCH = "touch"
    TABLET = "tablet"
    DESKTOP = "desktop"
    WIDESCREEN = "widescreen"
    FULLHD = "fullhd"


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


Text = TextBuilder()
