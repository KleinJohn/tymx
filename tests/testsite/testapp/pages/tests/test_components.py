import unittest

from typing_extensions import Any, override, Generator

from django_compose.base import Page, Router
from django_compose.base.components import Children, Component
from django_compose.base.components.base_components import BaseComponent
from django_compose.base.components.html_components import Div
from django_compose.base.context import Context


def traverse_df(component: "BaseComponent") -> "Generator[BaseComponent, None, None]":
    """Depth-first traversal generator for BaseComponent and its children."""
    yield component
    for child in component._children:
        yield from traverse_df(child)

def traverse_bf(component: "BaseComponent") -> "Generator[BaseComponent, None, None]":
    """Breadth-first traversal generator for BaseComponent and its children."""
    queue = [component]
    while queue:
        current = queue.pop(0)
        yield current
        queue.extend(current._children)


class KeywordAwareComponent(Component):

    def __init__(self, *args: Any, label: str = "", uppercase: bool = False, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.use_props(label=label, uppercase=uppercase)
        self.label = label
        self.uppercase = uppercase

    @override
    def build(self, context: Context, children: Children) -> Children:
        value = self.label.upper() if self.uppercase else self.label
        return Div[value, children]


class KwargsHandlingTests(unittest.TestCase):
    def test_custom_kwargs_are_handled_and_cloned(self) -> None:
        component = KeywordAwareComponent(label="hello", uppercase=True)["child"]

        self.assertEqual(component.label, "hello")
        self.assertTrue(component.uppercase)
        self.assertEqual(component.props, {"label": "hello", "uppercase": True})

        clone = component["again"]
        self.assertEqual(clone.label, "hello")
        self.assertTrue(clone.uppercase)

        context = Context(router=Router("test", pages=[Page(name="index")]))
        built = clone.full_build(context)

        self.assertIsNotNone(built)
        assert built is not None
        built_node = built[0] if isinstance(built, list) else built
        print(built_node.to_string(verbose=True))
        self.assertIn("HELLO", built_node.to_string(verbose=True))


if __name__ == "__main__":
    unittest.main()
