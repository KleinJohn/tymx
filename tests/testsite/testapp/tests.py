from django_compose.base.components.html_components import H1, Div, Span
from django_compose.base.components import Context


if __name__ == "__main__":
    elem = Div["Test1", Span[Div["Super"]], H1["Header"]]
    context = Context()
    print(elem.render(context))
