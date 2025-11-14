from django.http import HttpRequest, HttpResponse
from django_compose.base.page import DjangoApp, Page


home_page = Page(
    name="Home Page",
    body="Welcome to the Home Page!",
)

app = DjangoApp(starts_on=home_page)


# Create your views here.
def index(request: HttpRequest):
    return HttpResponse(app.render())
