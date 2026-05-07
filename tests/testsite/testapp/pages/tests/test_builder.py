import unittest

from typing import override

from django_compose.base.app import DjangoApp
import django_compose.base.components.html_components as html
from django_compose.base import Page, Router
from django_compose.base.attributes import classes, id, style
from django_compose.base.components import Component
from django_compose.base.helpers.debug import validate_is_built
from django_compose.base.context import Context
from django_compose.base.types import Children


class CustomButton(Component):

    @override
    def build(self, context: Context) -> Children:
        return html.Div[
            "Custom Button Start",
            html.Button[self.children],
            "End of Custom Button",
        ]


class CustomDiv(Component):

    @override
    def build(self, context: Context) -> Children:
        return html.Div[
            "Custom Div Start",
            CustomButton[self.children],
            CustomButton["Me too!", html.Input],
            "Custom Div End",
        ]


class BuilderRegressionTests(unittest.TestCase):
    def test_builds_components_returned_from_build(self) -> None:
        context = Context(
            Router(DjangoApp(name="testapp", pages=[]), pages=[]),
            Page(name="test", head=[]),
        )
        component = CustomDiv(
            [classes("custom-div"), id("custom-div-id")]
        ).with_attributes(style="color: red;")["Click Me!"]

        built_components = component.full_build(context)

        self.assertTrue(built_components)
        validate_is_built(built_components)


if __name__ == "__main__":
    unittest.main()
