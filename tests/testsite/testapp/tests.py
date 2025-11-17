from django_compose.base.components.html_components import H1, Div, Span, Input, Context
from django_compose.base.modifiers import styles, id
from django_compose.base.theme import Theme


if __name__ == "__main__":
    # elem = Div["Test1", Span[Div["Super"]], H1["Header"]]
    elem = H1(
        id("header1"),
        styles(color="blue", font_size="12px"),
    )[
        Div["Test1", Span[Div["Super"]]],
    ]
    theme_data = Theme()
    context = Context(theme_data)
    print(elem.render(context))
