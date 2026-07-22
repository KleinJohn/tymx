from typing import override

from tymx.base.components.compose_components import Page
import tymx.base.components.html_components as html
import tymx.base.attributes as a

from tymx.base.components.base_components import Component, NoChildren
from tymx.base.context import Context
from tymx.base.types import Children
from tymx.hx import State, StateChange, Stateful, on_click
from tymx import debug
from tymx.hx._state import state_field


class NameState(Stateful):
    is_charlie: State[bool] = state_field(default=False)
    selected: State[str] = state_field(default="Alice")

    def retrieve(self) -> StateChange[bool, bool]:
        # retrieve name from db...
        new_is_charlie = self.selected._value == "Charlie"
        return self.is_charlie.set(new_is_charlie)

    def change_selected(self) -> StateChange[str, str]:
        new_selected = "Charlie"
        return self.selected.set(new_selected)


class Nameplate(NoChildren, Component):

    def build_selection(self, context: Context, selected_name: str) -> Children:
        return html.Select[
            html.Option((a.value("Alice"), a.selected(selected_name == "Alice")))[
                "Alice"
            ],
            html.Option((a.value("Bob"), a.selected(selected_name == "Bob")))["Bob"],
            html.Option((a.value("Charlie"), a.selected(selected_name == "Charlie")))[
                "Charlie"
            ],
        ]

    @override
    def build(self, context: Context) -> Children:
        name_state = context.bind(NameState)
        return [
            html.Div[
                html.Span["Is the name Charlie?: "],
                name_state.is_charlie.as_text(lambda x: "Yes" if x else "No"),
            ],
            name_state.selected.as_template(self.build_selection),
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
    page = Page()[MyComponent]
    context = debug.get_context(page)
    built = page.full_build(context)[0]
    print(built.to_string(pretty=True, verbose=True))
    print(built.render())
