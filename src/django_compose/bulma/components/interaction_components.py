from enum import Enum

from typing_extensions import Any

from django_compose.base.attributes import Attribute, classes, disabled, type_
from django_compose.base.components import ModifiersOrAttributes, Children
from django_compose.base.components.base_components import Component
from django_compose.base.context import Context
import django_compose.base.components.html_components as html


class BulmaButtonType(str, Enum):
    BUTTON = "button"
    LINK = "link"
    SUBMIT = "submit"
    RESET = "reset"


class BulmaButtonColor(str, Enum):
    WHITE = "is-white"
    LIGHT = "is-light"
    DARK = "is-dark"
    BLACK = "is-black"
    TEXT = "is-text"
    GHOST = "is-ghost"
    PRIMARY = "is-primary"
    LINK = "is-link"
    INFO = "is-info"
    SUCCESS = "is-success"
    WARNING = "is-warning"
    DANGER = "is-danger"


class BulmaButtonColorScheme(str, Enum):
    DARK = "is-dark"
    LIGHT = "is-light"


class BulmaButtonSize(str, Enum):
    SMALL = "is-small"
    NORMAL = "is-normal"
    MEDIUM = "is-medium"
    LARGE = "is-large"


class BulmaButtonStyle(str, Enum):
    OUTLINED = "is-outlined"
    INVERTED = "is-inverted"
    ROUNDED = "is-rounded"


class BulmaButtonState(str, Enum):
    HOVERED = "is-hovered"
    FOCUSED = "is-focused"
    ACTIVE = "is-active"
    STATIC = "is-static"


class BulmaButtonAlignment(str, Enum):
    LEFT = "is-left"
    CENTERED = "is-centered"
    RIGHT = "is-right"


class BulmaButton(Component):

    def __init__(
        self,
        *modifiers: ModifiersOrAttributes,
        button_type: BulmaButtonType | str = BulmaButtonType.BUTTON,
        color: BulmaButtonColor | str | None = None,
        color_scheme: BulmaButtonColorScheme | str | None = None,
        size: BulmaButtonSize | str | None = None,
        style: BulmaButtonStyle | str | None = None,
        state: BulmaButtonState | str | None = None,
        responsive: bool = False,
        fullwidth: bool = False,
        loading: bool = False,
        disabled: bool = False,
        selected: bool = False,
        icon: Children = None,
        icon_size: BulmaButtonSize | str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*modifiers, **kwargs)
        self.use_props(
            button_type=button_type,
            color=color,
            color_scheme=color_scheme,
            size=size,
            style=style,
            state=state,
            responsive=responsive,
            fullwidth=fullwidth,
            loading=loading,
            disabled=disabled,
            selected=selected,
            icon=icon,
            icon_size=icon_size,
        )
        self.button_type = BulmaButtonType(button_type)
        self.color = BulmaButtonColor(color) if color else None
        self.color_scheme = (
            BulmaButtonColorScheme(color_scheme) if color_scheme else None
        )
        self.size = BulmaButtonSize(size) if size else None
        self.style = BulmaButtonStyle(style) if style else None
        self.state = BulmaButtonState(state) if state else None
        self.responsive = responsive
        self.fullwidth = fullwidth
        self.loading = loading
        self.disabled = disabled
        self.selected = selected
        self.icon = icon
        self.icon_size = BulmaButtonSize(icon_size) if icon_size else None

    def _get_attributes(self, context: Context) -> list[Attribute]:
        attrs: list[Attribute] = [classes("button")]
        if self.button_type == BulmaButtonType.SUBMIT:
            attrs.append(type_("submit"))
        elif self.button_type == BulmaButtonType.RESET:
            attrs.append(type_("reset"))
        if self.color:
            attrs.append(classes(self.color.value))
        if self.color_scheme:
            attrs.append(classes(self.color_scheme.value))
        if self.size:
            attrs.append(classes(self.size.value))
        if self.style:
            attrs.append(classes(self.style.value))
        if self.state:
            attrs.append(classes(self.state.value))
        if self.responsive:
            attrs.append(classes("is-responsive"))
        if self.fullwidth:
            attrs.append(classes("is-fullwidth"))
        if self.loading:
            attrs.append(classes("is-loading"))
        if self.disabled:
            attrs.append(disabled(True))
        if self.selected:
            attrs.append(classes("is-selected"))
        return attrs

    def build(self, context: Context, children: Children) -> Children:
        html_element: type[Component] = html.Button
        match self.button_type:
            case BulmaButtonType.BUTTON:
                html_element = html.Button
            case BulmaButtonType.LINK:
                html_element = html.A
            case BulmaButtonType.SUBMIT | BulmaButtonType.RESET:
                html_element = html.Input

        attrs = self._get_attributes(context)

        return html_element(*attrs)[
            (
                children
                if self.icon is None
                else (
                    html.Span(
                        classes("icon"),
                        classes(self.icon_size.value) if self.icon_size else None,
                    )[self.icon],
                    html.Span[children] if children else None,
                )
            )
        ]


class BulmaButtons(Component):
    def __init__(
        self,
        *modifiers: ModifiersOrAttributes,
        addons: bool = False,
        centered: BulmaButtonAlignment | str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*modifiers, **kwargs)
        self.use_props(addons=addons, centered=centered)
        self.addons = addons
        self.centered = BulmaButtonAlignment(centered) if centered else None

    def build(self, context: Context, children: Children) -> Children:
        attrs: list[Attribute] = []
        if self.addons:
            attrs.append(classes("has-addons"))
        if self.centered:
            attrs.append(classes(self.centered.value))
        return html.Div(*attrs)[children]
