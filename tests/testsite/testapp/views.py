from django.http import HttpRequest, HttpResponse
from django_compose.base.components.html_components import H1, Div
from django_compose.base.page import DjangoApp, Page
from django_compose.base.modifiers import styles, id


home_page = Page(
    name="Home Page",
    body=Div[
        H1(
            id("main-header"),
            styles(color="blue"),
        )["Welcome to the Home Page!"]
    ],
)

app = DjangoApp(starts_on=home_page)


# Create your views here.
def index(request: HttpRequest):
    return HttpResponse(app.render())
