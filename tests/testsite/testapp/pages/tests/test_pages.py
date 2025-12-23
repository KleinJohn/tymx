import unittest
from django_compose.base.components import (
    Component,
    Div,
    Button,
    A,
    H1,
    Input,
    Children,
)
from django_compose.base.context import Context
from django_compose.base.attributes import id, style, classes, disabled
from django_compose.base.app import Page, Router, Theme
from django_compose.base.modifiers import DebugModifier


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
        return A[children]


index_page = Page(
    name="index",
    route_pattern="",
    body=[
        H1((id("header1"), style(color="blue", font_size="12px")))[
            CustomDiv("button", "is-active")["press"],
        ],
        "An Input:",
        Input(classes("input-field"), style(margin="5px"), disabled),
    ],
)

service_page = Page(
    name="service",
    body=[
        H1("title", style("font-size:3em"))["Service Page"],
        IndexLink(DebugModifier())["Go to Index Page"],
    ],
)

if __name__ == "__main__":
    context = Context(
        router=Router("test", pages=[index_page, service_page]), theme=Theme()
    )
    built_index_page = index_page.full_build(context)
    built_service_page = service_page.full_build(context)
    print(built_index_page)
    print(built_service_page)
