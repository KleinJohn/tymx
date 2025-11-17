from django_compose.base.components import ThemedComponent, Component, Context
import django_compose.base.components.html_components as html


class Button(ThemedComponent):

    def build(self, context: Context) -> Component:
        return html.Button()
