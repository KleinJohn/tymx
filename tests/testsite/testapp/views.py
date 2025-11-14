from django.http import HttpRequest, HttpResponse
from django_compose.base.components import H1, P, Div
from django_compose.base.page import DjangoApp, Page

home_page = Page(
    name="Home Page",
    body=Div[
        H1["Welcome to the Test App"],
        P["This is a simple Django Compose application."],
    ],
)

app = DjangoApp(starts_on=home_page)


# Create your views here.
def index(request: HttpRequest):
    return HttpResponse(app.render())
