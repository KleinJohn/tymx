from __future__ import annotations

from typing import override

from attrs import field

import tymx.base.attributes as a
import tymx.base.components.html_components as html
from tymx.base.components import Component, ValidationError
from tymx.base.components.base_components import NoInheritance
from tymx.base.context import Context
from tymx.base.helpers import enum_converter, optional_enum_converter
from tymx.base.helpers.converters import (
    optional_string_like_converter,
    string_like_converter,
)
from tymx.base.helpers.validation import children_are_type, children_have_attribute
from tymx.base.types import Children
from tymx.bulma._colors import Color, color_converter

from ._types import (
    ButtonAlignment,
    ButtonState,
    ButtonStyle,
    ButtonType,
    ColorScheme,
    ImageSize,
    RowType,
    Side,
    Size,
)


class Block(Component):
    """Bulma's most basic spacer block.

    - `<element>[children]`

    See https://bulma.io/documentation/elements/block/ for details.
    """

    element: type[Component] = html.Div

    @override
    def build(self, context: Context) -> Children:
        return self.element(a.classes("block"))[self.children]


class Box(Component):
    """A white box to contain other elements.

    - `<element>[children]`

    See https://bulma.io/documentation/elements/box/ for details.
    """

    element: type[Component] = html.Div

    @override
    def build(self, context: Context) -> Children:
        return self.element(a.classes("box"))[self.children]


class Button(Component):
    """Bulma button component.

    Structure:
    - `<button|a|input>[children]` If `icon` is not provided
    - `<button|a|input>[icon, span[children]]` If `icon` is provided and icon_side = LEFT
    - `<button|a|input>[span[children], icon]` If `icon` is provided and icon_side = RIGHT

    `button_type` controls the rendered element:
    - `ButtonType.BUTTON` renders a `<button>` element.
    - `ButtonType.LINK` renders an `<a>` element.
    - `ButtonType.SUBMIT` and `ButtonType.RESET` render an `<input>` element.

    See https://bulma.io/documentation/elements/button/ for details.
    """

    button_type: ButtonType = field(
        default=ButtonType.BUTTON, converter=enum_converter(ButtonType)
    )
    color_scheme: ColorScheme | None = field(
        default=None, converter=optional_enum_converter(ColorScheme)
    )
    size: Size | None = field(default=None, converter=optional_enum_converter(Size))
    style: ButtonStyle | None = field(
        default=None, converter=optional_enum_converter(ButtonStyle)
    )
    state: ButtonState | None = field(
        default=None, converter=optional_enum_converter(ButtonState)
    )
    responsive: bool = False
    fullwidth: bool = False
    loading: bool = False
    disabled: bool = False
    selected: bool = False
    inverted: bool = False
    ghost: bool = False
    icon: Icon | None = None
    icon_size: None | Size = field(
        default=None,
        converter=optional_enum_converter(Size),
    )
    icon_side: Side = field(
        default=Side.LEFT,
        converter=enum_converter(Side),
    )

    def _get_element(self) -> type[Component]:
        html_element: type[Component] = html.Button
        match self.button_type:
            case ButtonType.BUTTON:
                html_element = html.Button
            case ButtonType.LINK:
                html_element = html.A
            case ButtonType.SUBMIT | ButtonType.RESET:
                html_element = html.Input
        return html_element

    def _get_attributes(self) -> list[a.Attribute]:
        attrs: list[a.Attribute] = [a.classes("button")]

        if self.button_type in (ButtonType.SUBMIT, ButtonType.RESET):
            attrs.append(a.type_(self.button_type))

        optional_classes = [
            self.color_scheme,
            self.size,
            self.style,
            self.state,
        ]
        attrs.extend(a.classes(cls) for cls in optional_classes if cls)

        boolean_classes = {
            self.responsive: "is-responsive",
            self.fullwidth: "is-fullwidth",
            self.loading: "is-loading",
            self.selected: "is-selected",
            self.inverted: "is-inverted",
            self.ghost: "is-ghost",
        }
        attrs.extend(a.classes(c) for active, c in boolean_classes.items() if active)

        if self.disabled:
            attrs.append(a.disabled(True))

        return attrs

    @override
    def build(self, context: Context) -> Children:
        Element = self._get_element()
        attrs = self._get_attributes()

        return Element(attrs)[
            (
                self.children
                if not self.icon
                else (
                    self.icon,
                    html.Span[self.children] if self.children else None,
                )[:: -1 if self.icon_side == Side.RIGHT else 1]
            )
        ]


class Buttons(Component):
    """Bulma buttons component for grouping multiple buttons.

    Structure:
    - `<div>[children]` where children are instances of `Button`

    See also:
        https://bulma.io/documentation/elements/button/#list-of-buttons
    """

    addons: bool = False
    alignment: ButtonAlignment | None = field(
        default=None, converter=optional_enum_converter(ButtonAlignment)
    )

    @override
    def _validate(self) -> None:
        super()._validate()
        if not all(isinstance(child, Button) for child in self.children):
            raise ValidationError("All children of Buttons must be instances of Button.")

    def _get_attributes(self) -> list[a.Attribute]:
        attrs: list[a.Attribute] = [a.classes("buttons")]
        if self.addons:
            attrs.append(a.classes("has-addons"))
        if self.alignment:
            attrs.append(a.classes(self.alignment))
        return attrs

    @override
    def build(self, context: Context) -> Children:
        attrs = self._get_attributes()
        return html.Div(attrs)[self.children]


class Content(Component):
    """A single class to handle WYSIWYG generated content, where only HTML tags are available.

    Structure:
    - `<element>[children]`

    See also:
        https://bulma.io/documentation/elements/content/
    """

    element: type[Component] = html.Div

    @override
    def build(self, context: Context) -> Children:
        return self.element(a.classes("content"))[self.children]


class Delete(Component):
    """A versatile delete cross.

    Structure:
    - `<button>[children]`

    See also:
        https://bulma.io/documentation/elements/delete/
    """

    size: Size | None = field(default=None, converter=optional_enum_converter(Size))

    @override
    def build(self, context: Context) -> Children:
        return html.Button(a.classes("delete"))[self.children]


class Icon(NoInheritance, Component):
    """A wrapper for icons.

    Structure:
    - `<span>[<i>(target)]` if no children are provided
    - `<span>[<span>[<i>(target)], <span>[children]]` if children are provided

    See also:
        https://bulma.io/documentation/elements/icon/
    """

    size: Size | None = field(default=None, converter=optional_enum_converter(Size))

    @override
    def build(self, context: Context) -> Children:
        inner_icon = html.Span(("icon", self.size))[html.I(self.target)]
        if self.children:
            return html.Span("icon-text")[
                inner_icon,
                html.Span[self.children],
            ]
        else:
            return inner_icon


class Image(Component):
    """A container for responsive images.

    Structure:
    - `<figure>[<img>(src)]` if no children are provided

    See also:
        https://bulma.io/documentation/elements/image/
    """

    src: str | None = None
    size: ImageSize | None = field(
        default=None, converter=optional_enum_converter(ImageSize)
    )
    rounded: bool = False
    fullwidth: bool = False

    @override
    def build(self, context: Context) -> Children:
        fig_attrs: list[a.Attribute] = [a.classes("image")]
        img_attrs: list[a.Attribute] = []
        if self.size:
            fig_attrs.append(a.classes(self.size))
        if self.src:
            img_attrs.append(a.src(self.src))
        if self.rounded:
            img_attrs.append(a.classes("is-rounded"))
        if self.fullwidth:
            img_attrs.append(a.classes("is-fullwidth"))

        return html.Figure(fig_attrs)[html.Img(img_attrs)]


class Notification(Component):
    """Bold notification blocks, to alert your users of something.

    Structure:
    - `<div>[children]`

    See also:
        https://bulma.io/documentation/elements/notification/
    """

    color: str | None = field(default=None, converter=color_converter(Color))

    @override
    def build(self, context: Context) -> Children:
        attrs: list[a.Attribute] = [a.classes("notification")]
        if self.color:
            attrs.append(a.classes(self.color))
        return html.Div(attrs)[self.children]


class ProgressBar(Component):
    """Native HTML progress bars."""

    value: str | None = field(converter=optional_string_like_converter, default=None)
    max_value: str = field(converter=string_like_converter, default="100")
    size: Size | None = field(default=None, converter=optional_enum_converter(Size))

    @override
    def build(self, context: Context) -> Children:
        classes: list[a.Attribute] = [a.classes("progress"), a.max(self.max_value)]
        if self.value is not None:
            classes.append(a.value(self.value))
        if self.size:
            classes.append(a.classes(self.size))

        return html.Progress(classes)[self.children]


class Table(Component):
    """The inevitable HTML table, with special case cells."""

    @override
    def _validate(self) -> None:
        super()._validate()
        if not children_are_type(self.children, [TableRow]):
            raise ValidationError("Children of Table have to be of type TableRow.")

    def _split_row_types(self) -> tuple[list[TableRow], list[TableRow], list[TableRow]]:
        head, body, foot = [], [], []
        for child in self.children:
            assert isinstance(child, TableRow)
            match child.row_type:
                case RowType.HEAD:
                    head.append(child)
                case RowType.BODY:
                    body.append(child)
                case RowType.FOOT:
                    foot.append(child)
        return head, body, foot

    @override
    def build(self, context: Context) -> Children:
        head, body, foot = self._split_row_types()
        return html.Table(a.classes("table"))[
            html.Thead[head],
            html.Tbody[body],
            html.Tfoot[foot],
        ] 


class TableRow(Component):

    row_type: RowType = RowType.BODY

    auto_wrap: bool = True
    """If True, children that are not <th> or <td> will be wrapped in <td>/<th> elements."""

    @override
    def build(self, context: Context) -> Children:
        content: list[Component] = []
        for child in self.children:
            if not self.auto_wrap or isinstance(child, (html.Th, html.Td)):
                content.append(child)
            elif self.row_type == RowType.HEAD:
                content.append(html.Th()[child])
            else:
                content.append(html.Td()[child])
        return html.Tr[content]


class Tag(Component):
    """Small tag labels to insert anywhere."""

    size: Size | None = field(default=None, converter=optional_enum_converter(Size))

    @override
    def build(self, context: Context) -> Children:
        classes: list[a.Attribute] = [a.classes("tag")]
        if self.size:
            classes.append(a.classes(self.size))
        return html.Span(*classes)[self.children]
    

class Tags(Component):
    """A container for multiple tags."""

    @override
    def _validate(self) -> None:
        super()._validate()
        if not children_are_type(self.children, [Tag]):
            raise ValidationError("Children of Tags have to be of type Tag.")

    @override
    def build(self, context: Context) -> Children:
        return html.Div(a.classes("tags"))[self.children]

