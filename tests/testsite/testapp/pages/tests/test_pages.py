from django_compose.base.components import (
    Component,
    Div,
    Button,
    Label,
    A,
    H1,
    Input,
    Children,
)
from django_compose.base.context import Context
from django_compose.base.attributes import id, style, classes, disabled
from django_compose.base.app import Page, Router, Theme
from django_compose.base.modifiers.debug_modifiers import (
    PrintComponentModifier,
    PrintContextModifier,
)


class CustomButton(Component):

    def build(self, context: Context, children: Children) -> Children:
        return Div[
            "Custom Button Start",
            children,
            "End of Custom Button",
        ]


class CustomDiv(Component):
    def build(self, context: Context, children: Children) -> Children:
        return [
            CustomButton[
                Div["Custom Div Start"],
                children,
                Div["Custom Div End"],
            ],
            Div["After custom button"],
        ]


class IndexLink(Component):
    def build(self, context: Context, children: Children) -> Children:
        return A[children]


index_page = Page(
    PrintContextModifier(),
    name="index",
    route_pattern="",
    body=[
        H1(id("header1"), style(color="blue", font_size="12px"))[
            CustomDiv("custom-div")[H1["press"]],
            IndexLink["Go to Service Page"],
        ],
        "An Input:",
        Input(classes("input-field"), style(margin="5px"), disabled),
    ],
)

service_page = Page(
    name="service",
    body=[
        H1("title", style("font-size:3em"))["Service Page"],
        IndexLink["Go to Index Page"],
    ],
)


def custom_label(context: Context, children: Children) -> Children:
    return [
        Div["Here: "],
        Label[children],
    ]


class CustomContent(Component):
    def build(self, context: Context, children: Children) -> Children:
        return [
            custom_label,
            Button(id("button"))["press"],
        ]


test_page = Page(
    PrintComponentModifier(),
    name="test",
    body=[
        H1["Title"],
        CustomContent("custom-content")["Label"],
    ],
)

if __name__ == "__main__":
    context = Context(router=Router("test", pages=[test_page]))
    built_test_page = test_page.full_build(context)
    # print(built_test_page.__str__(pretty=True, verbose=True))
