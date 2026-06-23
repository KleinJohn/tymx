from collections.abc import Sequence

from tymx.base.components.base_components import Component


def children_are_type(children: Sequence[Component], types: Sequence[type[Component]]):
    return all(any(isinstance(c, t) for t in types) for c in children)
