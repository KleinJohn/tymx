from enum import Enum

from typing_extensions import Any

from django_compose.base.components import ThemedComponent, Component
from django_compose.base.components.base_components import ModifierLike
from django_compose.base.theme import Theme, ThemeType

import django_compose.base.components.html_components as html
import django_compose.bulma.components as bulma


class ButtonStyle(str, Enum):
    REGULAR = "regular"
    OUTLINED = "outlined"
    FILLED = "filled"
    TONAL = "tonal"
    TEXT = "text"

    def __str__(self) -> str:
        return self.value


class Button(ThemedComponent):

    def __init__(
        self,
        *modifiers: ModifierLike,
        style: ButtonStyle | str = ButtonStyle.REGULAR,
        **kwargs: Any,
    ) -> None:
        super().__init__(*modifiers, **kwargs)
        self.use_props(style=style)
        self.style = str(style)

    def from_theme(
        self, theme: Theme, *smods: ModifierLike, **skwargs: Any
    ) -> Component:
        match theme.framework:
            case ThemeType.HTML:
                return html.Button(*smods, **skwargs)
            case ThemeType.BULMA:
                return bulma.BulmaButton(*smods, **skwargs)
            case _:
                raise ValueError(f"Unsupported theme framework: {theme.framework}")


class ButtonGroup(ThemedComponent):
    pass
