from __future__ import annotations

from attrs import field

from django_compose.base.components import Component
from django_compose.base.components.base_components import NoInheritance
from django_compose.base.context import Context
from django_compose.base.types import Children
from django_compose.base.helpers import enum_converter, optional_enum_converter

import django_compose.base.attributes as a
import django_compose.base.components.html_components as html
from django_compose.bulma._colors import Color, color_converter

from ._types import (
    ButtonType,
    ColorScheme,
    ButtonSize,
    ButtonStyle,
    ButtonState,
    ButtonAlignment,
    ImageSize,
    Side,
)


class Block(Component):
    """Bulma's most basic spacer block.

    - `<element>[children]`

    See https://bulma.io/documentation/elements/block/ for details.
    """

    element: type[Component] = html.Div

    def build(self, context: Context) -> Children:
        return self.element(a.classes("block"))[self.children]


class Box(Component):
    """A white box to contain other elements.

    - `<element>[children]`

    See https://bulma.io/documentation/elements/box/ for details.
    """

    element: type[Component] = html.Div

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
    color: str | None = field(default=None, converter=color_converter(Color))
    color_scheme: ColorScheme | None = field(
        default=None, converter=optional_enum_converter(ColorScheme)
    )
    size: ButtonSize | None = field(
        default=None, converter=optional_enum_converter(ButtonSize)
    )
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
    icon_size: None | ButtonSize = field(
        default=None,
        converter=optional_enum_converter(ButtonSize),
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
            self.color,
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

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if not all(isinstance(child, Button) for child in self.children):
            raise ValueError("All children of Buttons must be instances of Button.")

    def _get_attributes(self) -> list[a.Attribute]:
        attrs: list[a.Attribute] = [a.classes("buttons")]
        if self.addons:
            attrs.append(a.classes("has-addons"))
        if self.alignment:
            attrs.append(a.classes(self.alignment))
        return attrs

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

    def build(self, context: Context) -> Children:
        return self.element(a.classes("content"))[self.children]


class Delete(Component):
    """A versatile delete cross.

    Structure:
    - `<button>[children]`

    See also:
        https://bulma.io/documentation/elements/delete/
    """

    size: ButtonSize | None = field(
        default=None, converter=optional_enum_converter(ButtonSize)
    )

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

    size: ButtonSize | None = field(
        default=None, converter=optional_enum_converter(ButtonSize)
    )

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

    def build(self, context: Context) -> Children:
        attrs: list[a.Attribute] = [a.classes("notification")]
        if self.color:
            attrs.append(a.classes(self.color))
        return html.Div(attrs)[self.children]
