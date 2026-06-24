from collections.abc import Sequence

from tymx.base.components.base_components import Component
from tymx.base.attributes import Attribute


def children_are_type(children: Sequence[Component], types: Sequence[type[Component]]):
    return all(any(isinstance(c, t) for t in types) for c in children)


def children_have_attribute(children: Sequence[Component], attribute: Attribute):
    return all(attribute in c.attributes for c in children)
