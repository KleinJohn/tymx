from typing_extensions import Any, override, Self

from django_compose.base.components.base_components import Children, TemplateComponent
from django_compose.base.components.html_components import A
from django_compose.base.context import Context
from django_compose.base.attributes import href


class PageLink(TemplateComponent):
    def __init__(self, *args: Any, to: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.page_name = to

    @override
    def __getitem__(self, children: Children, **kwargs: Any) -> Self:
        return super().__getitem__(children, to=self.page_name, **kwargs)

    @override
    def build(self, context: Context, children: Children) -> Children:
        return A(href(context.router.navigate(self.page_name)))[children]
