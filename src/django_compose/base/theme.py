from django_compose.base.context import Consumable, ConsumerPolicy
from enum import Enum

from attrs import field


class ThemeType(str, Enum):
    HTML = "html"
    BULMA = "bulma"
    TAILWIND = "tailwind"
    MATERIAL = "material"

    def __str__(self) -> str:
        return self.value


class Theme(Consumable, frozen=True):
    consumer_policy = ConsumerPolicy.ALL_CHILDREN
    consume_first_matching = True

    framework: ThemeType = field(kw_only=False)
