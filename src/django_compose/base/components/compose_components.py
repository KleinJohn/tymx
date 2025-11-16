from django_compose.base.components import Component, Context
from django_compose.base.components.html_components import Button as HtmlButton


class Button(Component):

    def build(self, context: Context) -> Component:
        return HtmlButton()
