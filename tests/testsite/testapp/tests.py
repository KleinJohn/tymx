from django_compose.base.components import Component
from django_compose.base.components.base_components import (
    ComponentBaseChildren,
    Context,
)
from django_compose.base.components.html_components import H1, Button, Div, Span
from django_compose.base.modifiers import styles, id, disabled, classes, Attributes
from django_compose.base.page import Page
from django_compose.base.theme import Theme


class CustomButton(Component):

    def build(self, context: Context, children: ComponentBaseChildren) -> Component:
        return Div[
            "Custom Button",
            Button(disabled),
            "End of Custom Button",
            children,
        ]


def page_tests():
    page = Page(
        name="index",
        body=[
            H1((id("header1"), styles(color="blue", font_size="12px"), disabled))[
                Div[
                    "Test1",
                    Span[Div["Super"]],
                    CustomButton["Click Me"],
                ],
            ],
        ],
    )
    # TODO: find error, CustomButton's children are missing
    node = page.build(Context(theme=Theme()), children=Div)
    print(node)


def attribute_tests():
    attr1 = classes("btn", "btn-primary", "btn")
    attr2 = id("submit-button")
    attr3 = classes("btn-primary")
    attr4 = classes("active", "btn-primary")
    attr5 = styles(color="red", font_size="14px")
    attr6 = styles(margin="10px", font_size="16px")

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
