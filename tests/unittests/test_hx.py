from typing import override

from attrs import field

import tymx.base.components.html_components as html

from tymx.base.components.base_components import Component, NoChildren
from tymx.base.context import Context
from tymx.base.types import Children
from tymx.hx import State, StateChange, Stateful, state_converter, on_click
from tymx import debug


class NameState(Stateful):
    name: State[str] = field(default=State("Unknown"), converter=state_converter)

    def retrieve(self) -> StateChange[str, str]:
        # retrieve name from db...
        new_name = "New Name"
        return self.name.set(new_name)


class Nameplate(NoChildren, Component):

    @override
    def build(self, context: Context) -> Children:
        name_state = context.bind(NameState)
        return [
            html.Div[
                html.Span["The name is: "],
                str(name_state.name),
            ],
            html.Section["Second section"],
        ]


class MyComponent(Component):

    @override
    def build(self, context: Context) -> Children:
        name_state = context.use(NameState)
        return html.Div[
            Nameplate(),
            html.Button(on_click(name_state.retrieve))["Retrieve Name"],
            html.Section[html.Title["Here is some text:"], "Just some text"],
            self.children,
        ]


if __name__ == "__main__":
    component = MyComponent()
    context = debug.get_context(component)
    built = component.full_build(context)[0]
    print(built.to_string(pretty=True, verbose=True))
