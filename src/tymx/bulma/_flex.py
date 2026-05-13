from __future__ import annotations

from enum import StrEnum
from typing import Any

from attrs import define, field


class FlexDirection(StrEnum):
    ROW = "is-flex-direction-row"
    ROW_REVERSE = "is-flex-direction-row-reverse"
    COLUMN = "is-flex-direction-column"
    COLUMN_REVERSE = "is-flex-direction-column-reverse"


class FlexWrap(StrEnum):
    NOWRAP = "is-flex-wrap-nowrap"
    WRAP = "is-flex-wrap-wrap"
    WRAP_REVERSE = "is-flex-wrap-wrap-reverse"


class FlexJustifyContent(StrEnum):
    FLEX_START = "is-justify-content-flex-start"
    FLEX_END = "is-justify-content-flex-end"
    START = "is-justify-content-start"
    END = "is-justify-content-end"
    CENTER = "is-justify-content-center"
    SPACE_BETWEEN = "is-justify-content-space-between"
    SPACE_AROUND = "is-justify-content-space-around"
    SPACE_EVENLY = "is-justify-content-space-evenly"
    RIGHT = "is-justify-content-right"
    LEFT = "is-justify-content-left"


class FlexAlignContent(StrEnum):
    FLEX_START = "is-align-content-flex-start"
    FLEX_END = "is-align-content-flex-end"
    CENTER = "is-align-content-center"
    SPACE_BETWEEN = "is-align-content-space-between"
    SPACE_AROUND = "is-align-content-space-around"
    SPACE_EVENLY = "is-align-content-space-evenly"
    STRETCH = "is-align-content-stretch"
    START = "is-align-content-start"
    END = "is-align-content-end"
    BASELINE = "is-align-content-baseline"


class FlexAlignItems(StrEnum):
    STRETCH = "is-align-items-stretch"
    FLEX_START = "is-align-items-flex-start"
    FLEX_END = "is-align-items-flex-end"
    CENTER = "is-align-items-center"
    BASELINE = "is-align-items-baseline"
    START = "is-align-items-start"
    END = "is-align-items-end"
    SELF_START = "is-align-items-self-start"
    SELF_END = "is-align-items-self-end"


class FlexAlignSelf(StrEnum):
    AUTO = "is-align-self-auto"
    FLEX_START = "is-align-self-flex-start"
    FLEX_END = "is-align-self-flex-end"
    CENTER = "is-align-self-center"
    BASELINE = "is-align-self-baseline"
    STRETCH = "is-align-self-stretch"


def _shrink_grow_validator(instance: Any, attribute: Any, value: int | None) -> None:
    if value is not None and not (0 <= value <= 5):
        raise ValueError(f"{attribute} must be between 0 and 5, got {value}")


@define(kw_only=True, frozen=True, slots=False)
class FlexContainerBuilder(str):
    _direction: FlexDirection | None = field(alias="direction", default=None)
    _wrap: FlexWrap | None = field(alias="wrap", default=None)
    _justify_content: FlexJustifyContent | None = field(alias="justify_content", default=None)
    _align_content: FlexAlignContent | None = field(alias="align_content", default=None)
    _align_items: FlexAlignItems | None = field(alias="align_items", default=None)

    def __new__(
        cls,
        direction: FlexDirection | None = None,
        wrap: FlexWrap | None = None,
        justify_content: FlexJustifyContent | None = None,
        align_content: FlexAlignContent | None = None,
        align_items: FlexAlignItems | None = None,
    ):
        return super().__new__(
            cls,
            cls._container_from_values(
                direction=direction,
                wrap=wrap,
                justify_content=justify_content,
                align_content=align_content,
                align_items=align_items,
            ),
        )

    @classmethod
    def _container_from_values(
        cls,
        *,
        direction: FlexDirection | None = None,
        wrap: FlexWrap | None = None,
        justify_content: FlexJustifyContent | None = None,
        align_content: FlexAlignContent | None = None,
        align_items: FlexAlignItems | None = None,
    ) -> str:
        classes: list[str] = ["is-flex"]

        if direction is not None:
            classes.append(direction.value)
        if wrap is not None:
            classes.append(wrap.value)
        if justify_content is not None:
            classes.append(justify_content.value)
        if align_content is not None:
            classes.append(align_content.value)
        if align_items is not None:
            classes.append(align_items.value)

        return " ".join(classes)

    def container_with_values(
        self,
        *,
        direction: FlexDirection | None = None,
        wrap: FlexWrap | None = None,
        justify_content: FlexJustifyContent | None = None,
        align_content: FlexAlignContent | None = None,
        align_items: FlexAlignItems | None = None,
    ) -> FlexContainerBuilder:
        return FlexContainerBuilder(
            direction=direction or self._direction,
            wrap=wrap or self._wrap,
            justify_content=justify_content or self._justify_content,
            align_content=align_content or self._align_content,
            align_items=align_items or self._align_items,
        )

    @property
    def row(self) -> FlexContainerBuilder:
        return self.container_with_values(direction=FlexDirection.ROW)

    @property
    def row_reverse(self) -> FlexContainerBuilder:
        return self.container_with_values(direction=FlexDirection.ROW_REVERSE)

    @property
    def column(self) -> FlexContainerBuilder:
        return self.container_with_values(direction=FlexDirection.COLUMN)

    @property
    def column_reverse(self) -> FlexContainerBuilder:
        return self.container_with_values(direction=FlexDirection.COLUMN_REVERSE)

    # wrap properties
    @property
    def nowrap(self) -> FlexContainerBuilder:
        return self.container_with_values(wrap=FlexWrap.NOWRAP)

    @property
    def wrap(self) -> FlexContainerBuilder:
        return self.container_with_values(wrap=FlexWrap.WRAP)

    @property
    def reverse(self) -> FlexContainerBuilder:
        return self.container_with_values(wrap=FlexWrap.WRAP_REVERSE)

    # justify-content properties
    @property
    def justify_flex_start(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.FLEX_START)

    @property
    def justify_flex_end(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.FLEX_END)

    @property
    def justify_start(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.START)

    @property
    def justify_end(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.END)

    @property
    def justify_center(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.CENTER)

    @property
    def justify_space_between(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.SPACE_BETWEEN)

    @property
    def justify_space_around(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.SPACE_AROUND)

    @property
    def justify_space_evenly(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.SPACE_EVENLY)

    @property
    def justify_right(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.RIGHT)

    @property
    def justify_left(self) -> FlexContainerBuilder:
        return self.container_with_values(justify_content=FlexJustifyContent.LEFT)

    # align-content properties
    @property
    def align_content_flex_start(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.FLEX_START)

    @property
    def align_content_flex_end(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.FLEX_END)

    @property
    def align_content_center(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.CENTER)

    @property
    def align_content_space_between(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.SPACE_BETWEEN)

    @property
    def align_content_space_around(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.SPACE_AROUND)

    @property
    def align_content_space_evenly(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.SPACE_EVENLY)

    @property
    def align_content_stretch(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.STRETCH)

    @property
    def align_content_start(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.START)

    @property
    def align_content_end(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.END)

    @property
    def align_content_baseline(self) -> FlexContainerBuilder:
        return self.container_with_values(align_content=FlexAlignContent.BASELINE)

    # align-items properties
    @property
    def align_items_stretch(self) -> FlexContainerBuilder:
        return self.container_with_values(align_items=FlexAlignItems.STRETCH)

    @property
    def align_items_flex_start(self) -> FlexContainerBuilder:
        return self.container_with_values(align_items=FlexAlignItems.FLEX_START)

    @property
    def align_items_flex_end(self) -> FlexContainerBuilder:
        return self.container_with_values(align_items=FlexAlignItems.FLEX_END)

    @property
    def align_items_center(self) -> FlexContainerBuilder:
        return self.container_with_values(align_items=FlexAlignItems.CENTER)

    @property
    def align_items_baseline(self) -> FlexContainerBuilder:
        return self.container_with_values(align_items=FlexAlignItems.BASELINE)

    @property
    def align_items_start(self) -> FlexContainerBuilder:
        return self.container_with_values(align_items=FlexAlignItems.START)

    @property
    def align_items_end(self) -> FlexContainerBuilder:
        return self.container_with_values(align_items=FlexAlignItems.END)

    @property
    def align_items_self_start(self) -> FlexContainerBuilder:
        return self.container_with_values(align_items=FlexAlignItems.SELF_START)

    @property
    def align_items_self_end(self) -> FlexContainerBuilder:
        return self.container_with_values(align_items=FlexAlignItems.SELF_END)


@define(kw_only=True, frozen=True, slots=False)
class FlexChildBuilder(str):
    _align_self: FlexAlignSelf | None = field(alias="align_self", default=None)
    _flex_grow: int | None = field(
        validator=_shrink_grow_validator, default=None, alias="flex_grow"
    )
    _flex_shrink: int | None = field(
        validator=_shrink_grow_validator, default=None, alias="flex_shrink"
    )

    def __new__(
        cls,
        align_self: FlexAlignSelf | None = None,
        flex_grow: int | None = None,
        flex_shrink: int | None = None,
    ):
        return super().__new__(
            cls,
            cls._child_from_values(
                align_self=align_self,
                flex_grow=flex_grow,
                flex_shrink=flex_shrink,
            ),
        )

    @classmethod
    def _child_from_values(
        cls,
        *,
        align_self: FlexAlignSelf | None = None,
        flex_grow: int | None = None,
        flex_shrink: int | None = None,
    ) -> str:
        classes: list[str] = []

        if align_self is not None:
            classes.append(align_self.value)
        if flex_grow is not None:
            classes.append(f"is-flex-grow-{flex_grow}")
        if flex_shrink is not None:
            classes.append(f"is-flex-shrink-{flex_shrink}")

        return " ".join(classes)

    def child_with_values(
        self,
        *,
        align_self: FlexAlignSelf | None = None,
        flex_grow: int | None = None,
        flex_shrink: int | None = None,
    ) -> FlexChildBuilder:
        return FlexChildBuilder(
            align_self=align_self or self._align_self,
            flex_grow=self._flex_grow if flex_grow is None else flex_grow,
            flex_shrink=self._flex_shrink if flex_shrink is None else flex_shrink,
        )

    @property
    def align_self_auto(self) -> FlexChildBuilder:
        return self.child_with_values(align_self=FlexAlignSelf.AUTO)

    @property
    def align_self_flex_start(self) -> FlexChildBuilder:
        return self.child_with_values(align_self=FlexAlignSelf.FLEX_START)

    @property
    def align_self_flex_end(self) -> FlexChildBuilder:
        return self.child_with_values(align_self=FlexAlignSelf.FLEX_END)

    @property
    def align_self_center(self) -> FlexChildBuilder:
        return self.child_with_values(align_self=FlexAlignSelf.CENTER)

    @property
    def align_self_baseline(self) -> FlexChildBuilder:
        return self.child_with_values(align_self=FlexAlignSelf.BASELINE)

    @property
    def align_self_stretch(self) -> FlexChildBuilder:
        return self.child_with_values(align_self=FlexAlignSelf.STRETCH)

    def grow(self, value: int) -> FlexChildBuilder:
        return self.child_with_values(flex_grow=value)

    def shrink(self, value: int) -> FlexChildBuilder:
        return self.child_with_values(flex_shrink=value)


@define(kw_only=True, frozen=True, slots=False)
class FlexBuilder(FlexContainerBuilder, FlexChildBuilder):
    """Combines container and child flex properties without adding new attributes."""

    def __new__(cls):
        return str.__new__(cls, "")


Flex = FlexBuilder()
