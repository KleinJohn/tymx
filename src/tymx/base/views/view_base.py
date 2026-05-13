from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.views import View

if TYPE_CHECKING:
    from tymx.base.components.base_components import Component


class ComponentView(View):
    component: Component | None = None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self.component:
            return HttpResponseNotFound("Component is not built.")
        return HttpResponse(self.component.render())
