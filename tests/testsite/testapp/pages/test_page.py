from django_compose.base.components import Component, Children
from django_compose.base.components.html_components import H1, Button, Div, Input
from django_compose.base.attributes import disabled, id, styles, classes
from django_compose.base.modifiers.base_modifiers import DebugModifier
from django_compose.base.page import Context, Page


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


index_page = Page(
    name="index",
    body=[
        H1((id("header1"), styles(color="blue", font_size="12px"), disabled))[
            CustomDiv("button", "is-active", DebugModifier())[
                "Click Me",
                Input(classes("input-field"), styles(margin="5px")),
            ],
        ],
    ],
)
