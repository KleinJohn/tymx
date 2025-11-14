from django.http import HttpRequest, HttpResponse

# Create your views here.


def testview(request: HttpRequest):
    # result = home_page.render()
    return HttpResponse()
