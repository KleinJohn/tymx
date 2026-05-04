from enum import StrEnum


class ButtonType(StrEnum):
    BUTTON = "button"
    LINK = "link"
    SUBMIT = "submit"
    RESET = "reset"


class ButtonColor(StrEnum):
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


class ButtonColorScheme(StrEnum):
    DARK = "is-dark"
    LIGHT = "is-light"


class ButtonSize(StrEnum):
    SMALL = "is-small"
    NORMAL = "is-normal"
    MEDIUM = "is-medium"
    LARGE = "is-large"


class ButtonStyle(StrEnum):
    OUTLINED = "is-outlined"
    INVERTED = "is-inverted"
    ROUNDED = "is-rounded"


class ButtonState(StrEnum):
    HOVERED = "is-hovered"
    FOCUSED = "is-focused"
    ACTIVE = "is-active"
    STATIC = "is-static"


class ButtonAlignment(StrEnum):
    LEFT = "is-left"
    CENTERED = "is-centered"
    RIGHT = "is-right"
