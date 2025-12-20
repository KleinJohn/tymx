from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
import htpy


class ComposeView(View):
    content: htpy.Renderable | None = None

    def get(self, request, *args, **kwargs):
        if not self.content:
            return HttpResponseNotFound("Page is not built.")
        return HttpResponse(self.content)
