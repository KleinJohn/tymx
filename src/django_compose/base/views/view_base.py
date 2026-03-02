from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.views import View
from typing_extensions import Any

if TYPE_CHECKING:
    from django_compose.base.app import Page


class ComposePageView(View):
    page: Page | None = None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self.page:
            return HttpResponseNotFound("Page is not built.")
        return HttpResponse(self.page.render())
