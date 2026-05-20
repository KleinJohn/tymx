from tymx.base.components import Component
from tymx.base.components.base_components import (
    Children,
    Context,
)
from tymx.base.components.html_components import A, H1, Button, Div, Input
from tymx.base.attributes import classes, disabled, id, style
from tymx.base.modifiers import Attributes, DebugModifier
from tymx.base.app import Page
from tymx.base.router import AbstractRouter
from tymx.base.theme import Theme


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


def page_tests():
    index_page = Page(
        name="index",
        body=[
            H1((id("header1"), style(color="blue", font_size="12px"), disabled))[
                CustomDiv("button", "is-active", DebugModifier())[
                    "Click Me",
                    Input(classes("input-field"), style(margin="5px")),
                ],
            ],
        ],
    )
    home_page = Page(
        name="home",
        body=lambda context: [
            H1((id("header1"), style(color="blue", font_size="12px"), disabled))[
                CustomDiv(
                    ("button", "is-active"),
                    DebugModifier(),
                )[
                    "Click Me",
                    Input(classes("input-field"), style(margin="5px")),
                    # A(context.router.navigate("index"))["Back to Index"],
                ],
            ],
        ],
    )
    title = H1("title", style("font-size:3em"), DebugModifier())["Service Page"]
    context = Context(
        theme=Theme(), router=AbstractRouter(pages=[home_page, index_page])
    )
    # print(home_page.render())


def attribute_tests():
    attr1 = classes("btn btn-primary btn")
    attr2 = id("submit-button")
    attr3 = classes("btn-primary")
    attr4 = classes("active", "btn-primary")
    attr5 = style(color="red", font_size="14px")
    attr6 = style(margin="10px", font_size="16px")

    attrs = Attributes(attr1, attr2, attr3)
    print("Before adding attr4:", attrs)
    attrs.add(attr4)
    print("After adding attr5:", attrs)
    attrs.add(attr5)
    print("After adding attr6:", attrs)
    attrs.add(attr6)
    print("After adding att6:", attrs)
    print("Final attribute values:", attrs.values())


if __name__ == "__main__":
    page_tests()
