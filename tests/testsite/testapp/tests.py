from django_compose.base.components.html_components import H1, Div, Span
from django_compose.base.components import Context
from django_compose.base.modifiers import styles, id


if __name__ == "__main__":
    # elem = Div["Test1", Span[Div["Super"]], H1["Header"]]
    elem = H1(
        id("header1"),
        styles(color="blue", font_size="12px"),
    )[
        "Test1",
    ]
    context = Context()
    print(elem.render(context))
