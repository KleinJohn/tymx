from __future__ import annotations

from typing import Generator
import unittest

from tymx import bulma
from tymx.base.components import ValidationError
from tymx.base.components.base_components import Component
from tymx.base.modifiers.component_modifiers import NoValidation


def traverse_df(component: Component) -> Generator[Component, None, None]:
    """Depth-first traversal generator for BaseComponent and its children."""
    yield component
    for child in component.children:
        yield from traverse_df(child)


def traverse_bf(component: Component) -> Generator[Component, None, None]:
    """Breadth-first traversal generator for BaseComponent and its children."""
    queue = [component]
    while queue:
        current = queue.pop(0)
        yield current
        queue.extend(current.children)


class TestComponentValidation(unittest.TestCase):

    def test_validation_errors_raise_validation_error(self):
        with self.assertRaises(ValidationError):
            bulma.Tags[bulma.Button()]

    def test_no_validation_flag(self):
        bulma.Tags(NoValidation())[bulma.Button()]


if __name__ == "__main__":
    unittest.main()
