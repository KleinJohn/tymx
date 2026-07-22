from __future__ import annotations

from typing import ClassVar, override, TYPE_CHECKING

from attrs import field

if TYPE_CHECKING:
    from tymx.base.components import Component
    from tymx.base.context import Context

import tymx.base.attributes as a

from tymx.base.modifiers.base_modifiers import Modifier
from tymx.base.consumable import ConsumerPolicy


class NoValidation(Modifier):
    """
    A modifier that disables validation for a component and its children.
    """

    consumer_policy = ConsumerPolicy.NONE

    @override
    def post_init(self, component: Component) -> None:
        object.__setattr__(component, "do_validation", False)


class Key(Modifier):
    consumer_policy: ClassVar[ConsumerPolicy] = ConsumerPolicy.NONE
    __key_counter__: ClassVar[int] = 0
    _value: int = field(init=False, factory=lambda: Key._get_next_key())

    @classmethod
    def _get_next_key(cls) -> int:
        cls.__key_counter__ += 1
        return cls.__key_counter__

    def as_attribute(self) -> a.Attribute:
        return a.id(self.as_id())

    def as_id(self) -> str:
        return f"component-{self._value}"

    @override
    def transform(self, context: Context, result: list[Component]) -> list[Component]:
        assert len(result) == 1, "Key can only be applied to a single component"
        result[0] = result[0](self.as_attribute())
        return result
