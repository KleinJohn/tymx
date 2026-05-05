from __future__ import annotations

from typing import Generator
import unittest

from django_compose.base.components.base_components import Component


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


if __name__ == "__main__":
    unittest.main()
