from django.http import HttpRequest, HttpResponse
from tymx.base.components.html_components import H1, Button, Div, Span
from tymx.base.app import DjangoApp, Page
from tymx.base.modifiers import styles, id, disabled

index_page = Page(
    name="index",
    body=[
        H1((id("header1"), styles(color="blue", font_size="30px")))[
            "Meine Überschrift",
        ],
        Div[
            "Test1",
            Span[Div["Super"]],
            Button(disabled)["Can't click me!"],
        ],
    ],
)

app = DjangoApp(pages=[index_page])


# Create your views here.
def index(request: HttpRequest):
    return HttpResponse(app.render())
