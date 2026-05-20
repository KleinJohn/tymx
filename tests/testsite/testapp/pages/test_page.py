from tymx import bulma
from tymx.base.components.base_components import (
    Component,
    children_to_tuple,
    wrap_components,
)
from tymx.base.attributes import disabled, id, style, classes
from tymx.base.app import Page
from tymx.base.context import Context
from tymx.base.helpers.debug import validate_is_built
from tymx.base.modifiers.debug_modifiers import (
    PrintComponentsModifier,
    PrintContextModifier,
)
from tymx.base.types import Children
from tymx.django import App, Router

import tymx.base.components.html_components as html

from attrs import field


class CustomButton(Component):

    def build(self, context: Context) -> Children:
        return html.Div[
            "Custom Button Start",
            lambda context: html.Button[self.children],
            "End of Custom Button",
        ]


class CustomDiv(Component):

    test_children: tuple[Component, ...] = field(converter=children_to_tuple)

    def build(self, context: Context) -> Children:
        return [
            "Custom Div Start",
            self.test_children,
            html.Div("custom-div-class"),
            CustomButton("custom-button-test")[self.children],
            CustomButton["Me too!", html.Input],
            "Custom Div End",
        ]


index_page = Page(
    (PrintComponentsModifier(), classes("index-page")),
)[
    CustomDiv(
        [classes("custom-div"), id("custom-div-id")],
        test_children=html.Div("test-children"),
    )[html.Button()](
        id("overwritten-div-id"),
    )
]


class TestComponent(Component):

    def build(self, context: Context) -> Children:
        button_prototype = bulma.Button(size="is-large")
        return bulma.Block(element=html.Section)[
            bulma.Buttons[button_prototype(size=bulma.Size.MEDIUM), button_prototype]
        ]


# test_component = TestComponent("test-class")
test_component = TestComponent(classes("test-class"))

# built_component = wrap_components(test_component.full_build(context))
# validate_is_built([built_component])
# print(built_component.to_string(verbose=True, pretty=True))
# print(built_component.render())


# router = Router("testapp", pages=[])
# context = Context(router, Page())
# print("created context")
# custom_div = CustomDiv()
# print("created custom div")
# result = custom_div.full_build(context)
# print("built custom div")
# print(result)


# index_page = Page(
#     name="index",
#     route_pattern="",
#     data=[TimeData(time="12:00", in_hours=12)],
#     head=[],
#     body=[
#         H1((id("header1"), style(color="blue", font_size="12px")))[
#             CustomDiv("button is-active button")["press"],
#         ],
#         "An Input:",
#         Input(classes("input-field"), style(margin="5px"), disabled),
#         PageLink(to="service")["Go to Service Page"],
#     ],
# )

# service_page = Page(
#     name="service",
#     head=[],
#     body=[
#         H1("title", style="font-size:3em;font-size:3em")["Service Page"],
#         PageLink(to="index")["Go to Index Page"],
#     ],
# )
