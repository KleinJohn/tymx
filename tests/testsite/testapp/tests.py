from django_compose.base.components.html_components import H1, Div, Span
from django_compose.base.components import Context


if __name__ == "__main__":
    elem = Div[Span[Div["Hallo"]], H1["Super Titel"]]
    context = Context()
    print(elem.full_build(context))
