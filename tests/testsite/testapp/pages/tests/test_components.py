import unittest

from typing_extensions import Any, override, Generator

from django_compose.base import Page, Router
from django_compose.base.components import Children, Component, Component
from django_compose.base.components.html_components import Div
from django_compose.base.context import Context
from django_compose.bulma.components import BulmaButton
from django_compose.bulma.components.interaction_components import (
    BulmaButtonColor,
    BulmaButtonColorScheme,
    BulmaButtonType,
)

import django_compose.base.components.html_components as html


def traverse_df(component: "Component") -> "Generator[Component, None, None]":
    """Depth-first traversal generator for BaseComponent and its children."""
    yield component
    for child in component._children:
        yield from traverse_df(child)


def traverse_bf(component: "Component") -> "Generator[Component, None, None]":
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

        index = Page(name="index", head=[], body=[clone])
        context = Context(router=Router("test", pages=[index]))
        built = clone.full_build(context)

        self.assertIsNotNone(built)
        assert built is not None
        built_node = built[0] if isinstance(built, list) else built
        print(built_node.to_string(verbose=True))
        self.assertIn("HELLO", built_node.to_string(verbose=True))


class BulmaTest(unittest.TestCase):

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.context = Context(router=Router("test", pages=[]))

    def test_bulma_button1(self) -> None:
        button = BulmaButton(
            button_type=BulmaButtonType.SUBMIT,
            fullwidth=True,
            loading=True,
            disabled=True,
        )
        built = button.full_build(self.context)
        expected = html.Input(
            "button is-fullwidth is-loading", type_="submit", disabled=True
        ).full_build(self.context)
        assert isinstance(built, Component) and isinstance(expected, Component)
        print("Built:", built.to_string(verbose=True))
        print("Expected:", expected.to_string(verbose=True))
        self.assertEqual(built, expected)

    def test_bulma_button2(self) -> None:
        button = BulmaButton(
            button_type=BulmaButtonType.BUTTON,
            color=BulmaButtonColor.DANGER,
            size="is-large",
            color_scheme=BulmaButtonColorScheme.LIGHT,
            responsive=True,
            selected=True,
        )["Push Me"].full_build(self.context)
        expected = html.Button("button is-danger is-light is-large is-responsive is-selected")[
            "Push Me"
        ].full_build(self.context)
        assert isinstance(button, Component) and isinstance(expected, Component)
        print("Built:", button.to_string(verbose=True))
        print("Expected:", expected.to_string(verbose=True))
        self.assertEqual(button, expected)

    def test_bulma_button_wrong_enum_values(self) -> None:
        with self.assertRaises(ValueError):
            BulmaButton(button_type="invalid_type")
        with self.assertRaises(ValueError):
            BulmaButton(color=BulmaButtonColor("unknown_color"))


if __name__ == "__main__":
    unittest.main()
