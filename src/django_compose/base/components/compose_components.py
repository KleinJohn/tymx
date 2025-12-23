from typing import override
from django_compose.base.components.base_components import Children, Component
from django_compose.base.components.html_components import *
from django_compose.base.context import Context


class PageLink(Component):

    def __init__(self, *args, page_name: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.page_name = page_name

    @override
    def build(self, context: Context, children: Children) -> Children:
        return A(context.router.navigate(self.page_name))[children]
