from __future__ import annotations

from typing import override, TYPE_CHECKING

if TYPE_CHECKING:
    from tymx.base.components import Component

from tymx.base.modifiers.base_modifiers import Modifier
from tymx.base.consumable import ConsumerPolicy


class NoValidation(Modifier):
    """
    A modifier that disables validation for a component and its children.
    """

    consumer_policy = ConsumerPolicy.NONE

    @override
    def post_init(self, component: Component) -> None:
        object.__setattr__(component, "__validate__", False)

    