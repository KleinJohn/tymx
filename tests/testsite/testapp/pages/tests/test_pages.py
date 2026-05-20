from tymx.base.app import AbstractApp
from tymx.base.components import Component
from tymx.base.components.base_components import wrap_components
from tymx.base.types import Children
from tymx.base.components.html_components import (
    Div,
    Button,
    Label,
    A,
    H1,
    Input,
)
from tymx.base.context import Context
from tymx.base.attributes import id, style, classes, disabled
from tymx.base import Page, AbstractRouter


class CustomButton(Component):

    def build(self, context: Context) -> Children:
        return Div[
            "Custom Button Start",
            self.children,
            "End of Custom Button",
        ]


class CustomDiv(Component):
    def build(self, context: Context) -> Children:
        return [
            CustomButton[
                Div["Custom Div Start"],
                self.children,
                Div["Custom Div End"],
            ],
            Div["After custom button"],
        ]


class IndexLink(Component):
    def build(self, context: Context) -> Children:
        return A[self.children]


index_page = Page(name="index", route_pattern="")[
    H1((id("header1"), style(color="blue", font_size="12px")))[
        CustomDiv("custom-div")[H1["press"]],
        IndexLink["Go to Service Page"],
    ],
    "An Input:",
    Input((classes("input-field"), style(margin="5px"), disabled)),
]

service_page = Page(name="service")[
    H1(("title", style("font-size:3em")))["Service Page"],
    IndexLink["Go to Index Page"],
]


def custom_label(context: Context) -> Children:
    return [
        Div("custom-div")[Div("custom-div-inner")["Here: "]],
        Label,
    ]


class CustomContent(Component):
    def build(self, context: Context) -> Children:
        return [
            custom_label,
            Button(id("button"))[self.children],
        ]


test_page = Page(name="test")[
    H1["Title"],
    CustomContent("custom-content")["Label"],
]


if __name__ == "__main__":
    context = Context(
        router=AbstractRouter(AbstractApp(name="test", pages=[]), pages=[test_page])
    )
    built_test_page = wrap_components(test_page.full_build(context))
    print(built_test_page.to_string(pretty=True, verbose=True))
