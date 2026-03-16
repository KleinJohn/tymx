from typing_extensions import Any, override

from django_compose.base.components.base_components import Children, TemplateComponent
from django_compose.base.components.html_components import A
from django_compose.base.context import Context
from django_compose.base.attributes import href


class PageLink(TemplateComponent):
    def __init__(self, *args: Any, to: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.use_props(to=to)
        self.to = to

    @override
    def build(self, context: Context, children: Children) -> Children:
        return A(href(context.router.navigate(self.to)))[children]
