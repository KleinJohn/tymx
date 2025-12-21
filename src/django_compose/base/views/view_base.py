from __future__ import annotations
from typing import TYPE_CHECKING
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View

if TYPE_CHECKING:
    from django_compose.base.app import Page


class ComposePageView(View):
    page: Page | None = None

    def get(self, request, *args, **kwargs):
        print(self.page)
        if not self.page:
            return HttpResponseNotFound("Page is not built.")
        return HttpResponse(self.page.render())
