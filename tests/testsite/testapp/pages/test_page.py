from attrs import evolve, fields

from django_compose.base.components.base_components import (
    BuildData,
    Component,
    Fragment,
    wrap_components,
)
from django_compose.base.components.html_components import (
    A,
    H1,
    Button,
    Div,
    Input,
)
from django_compose.base.attributes import (
    disabled,
    id,
    style,
    classes,
)
from django_compose.base.modifiers import Modifier, Modifiers
from django_compose.base.app import Page
from django_compose.base.context import Context
from django_compose.base.modifiers.debug_modifiers import PrintComponentsModifier
from django_compose.base.router import Router
from django_compose.base.types import Children


# class TimeData(ContextData):
#     time: str | None = None
#     in_hours: int | None = None


class CustomButton(Component):

    def build(self, build: BuildData, children: Children) -> Children:
        return Div[
            "Custom Button Start",
            Button[children],
            "End of Custom Button",
        ]


class CustomDiv(Component):

    def build(self, build: BuildData, children: Children) -> Children:
        return Div[
            "Custom Div Start",
            children,
            "Custom Div End",
        ]


context = Context(Router("testapp", pages=[]), Page())
component = CustomDiv(
    [
        classes("custom-div"),
        id("custom-div-id"),
        PrintComponentsModifier(),
    ]
).with_attributes(style="color: red;")[CustomButton["Click Me!"]]
built_component = wrap_components(component.full_build(context))
print(built_component.attributes)
# print(built_component.to_string(verbose=True, pretty=True))


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
