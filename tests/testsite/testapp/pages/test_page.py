from django_compose.base.components import Component, Children
from django_compose.base.components.html_components import A, H1, Button, Div, Input
from django_compose.base.attributes import disabled, id, style, classes
from django_compose.base.modifiers.compose_modifiers import DebugModifier
from django_compose.base.app import Context, Page


class CustomButton(Component):

    def build(self, context: Context, children: Children) -> Children:
        return Div[
            "Custom Button Start",
            Button[children],
            "End of Custom Button",
        ]


class CustomDiv(Component):
    def build(self, context: Context, children: Children) -> Children:
        return Div[
            ["Custom Div Start"],
            CustomButton(disabled)[children],
            "Custom Div End",
        ]


class IndexLink(Component):
    def build(self, context: Context, children: Children) -> Children:
        return A(context.router.navigate("index"))[children]


index_page = Page(
    name="index",
    route_pattern="",
    body=lambda context: [
        H1((id("header1"), style(color="blue", font_size="12px")))[
            CustomDiv("button", "is-active")["press"],
        ],
        "Click Me",
        Input(classes("input-field"), style(margin="5px"), disabled),
        A(context.router.navigate("service"))["Go to service page"],
    ],
)

service_page = Page(
    name="service",
    body=[
        H1("title", style("font-size:3em"), DebugModifier())["Service Page"],
        IndexLink["Go to Index Page"],
    ],
)
