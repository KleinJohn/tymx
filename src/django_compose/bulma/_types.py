from enum import StrEnum


class ButtonType(StrEnum):
    BUTTON = "button"
    LINK = "link"
    SUBMIT = "submit"
    RESET = "reset"


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


class ImageSize(StrEnum):
    IS_16 = "is-16x16"
    IS_24 = "is-24x24"
    IS_32 = "is-32x32"
    IS_48 = "is-48x48"
    IS_64 = "is-64x64"
    IS_96 = "is-96x96"
    IS_128 = "is-128x128"


class ImageRatio(StrEnum):
    IS_SQUARE = "is-square"
    IS_1_BY_1 = "is-1by1"
    IS_5_BY_4 = "is-5by4"
    IS_4_BY_3 = "is-4by3"
    IS_3_BY_2 = "is-3by2"
    IS_5_BY_3 = "is-5by3"
    IS_16_BY_9 = "is-16by9"
    IS_2_BY_1 = "is-2by1"
    IS_3_BY_1 = "is-3by1"
    IS_4_BY_5 = "is-4by5"
    IS_3_BY_4 = "is-3by4"
    IS_2_BY_3 = "is-2by3"
    IS_3_BY_5 = "is-3by5"
    IS_9_BY_16 = "is-9by16"
    IS_1_BY_2 = "is-1by2"
    IS_1_BY_3 = "is-1by3"
