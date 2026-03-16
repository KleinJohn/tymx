import unittest

from typing_extensions import Any, override

from django_compose.base import Page, Router
from django_compose.base.attributes import classes, style
from django_compose.base.components import Children, Component
from django_compose.base.components.html_components import Div
from django_compose.base.context import Context


class CustomComponent(Component):

    @override
    def build(self, context: Context, children: Children) -> Children:
        return Div[children]


def make_context() -> Context:
    return Context(router=Router("test", pages=[Page(name="index")]))


class AttributeFromKwargsTests(unittest.TestCase):

    def test_attributes_present_on_built_component(self) -> None:
        component1 = CustomComponent(style="color:green", disabled=True)["child"]
        built1 = component1.full_build(make_context())

        assert built1 is not None
        built_node1 = built1[0] if isinstance(built1, list) else built1
        verbose1 = built_node1.to_string(verbose=True)
        
        print(verbose1)
        self.assertIn("style", built_node1.attributes)
        self.assertIn("disabled", built_node1.attributes)
        self.assertIn("color:green", verbose1)
        self.assertIn("disabled", verbose1)

        component2 = CustomComponent(classes="first second")[Div["nested child"]]
        built2 = component2.full_build(make_context())
        
        assert built2 is not None
        built_node2 = built2[0] if isinstance(built2, list) else built2
        verbose2 = built_node2.to_string(verbose=True)
        
        print(verbose2)
        self.assertIn("class", built_node2.attributes)
        self.assertIn("first", built_node2.attributes["class"])
        self.assertIn("second", built_node2.attributes["class"])
        self.assertIn("first", verbose2)
        self.assertIn("second", verbose2)


    def test_no_attributes_when_kwargs_empty(self) -> None:
        component = CustomComponent()
        self.assertFalse(bool(component.attributes))


if __name__ == "__main__":
    unittest.main()
