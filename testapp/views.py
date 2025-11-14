from django.http import HttpRequest, HttpResponse
from testapp.components.base import home_page
from compose.base import Context

# Create your views here.


def testview(request: HttpRequest):
    result = home_page.render()
    print(str(home_page.body.render(Context())))
    return HttpResponse(result)
