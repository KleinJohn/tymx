from django_compose.base.components.base_components import Component, wrap_components
from django_compose.base.attributes import disabled, id, style, classes
from django_compose.base.app import Page
from django_compose.base.context import Context
from django_compose.base.helpers.debug import validate_is_built
from django_compose.base.modifiers.debug_modifiers import (
    PrintComponentsModifier,
    PrintContextModifier,
)
from django_compose.base.router import Router
from django_compose.base.types import Children

import django_compose.base.components.html_components as html


class CustomButton(Component):

    def build(self, context: Context) -> Children:
        return html.Div[
            "Custom Button Start",
            html.Button[self.children],
            "End of Custom Button",
        ]


class CustomDiv(Component):

    def build(self, context: Context) -> Children:
        return [
            "Custom Div Start",
            html.Div("custom-div-class"),
            CustomButton("custom-button-test")[self.children],
            CustomButton["Me too!", html.Input],
            "Custom Div End",
        ]


context = Context(Router("testapp", pages=[]), Page())
component = CustomDiv([classes("custom-div"), id("custom-div-id")]).with_attributes(
    style="color: red;"
)[html.Input()]

built_components = component.full_build(context)
validate_is_built(built_components)
print(wrap_components(built_components).to_string(verbose=True, pretty=True))


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
