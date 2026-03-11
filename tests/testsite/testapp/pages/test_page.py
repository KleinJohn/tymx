from django_compose.base.components import Component, Children
from django_compose.base.components.html_components import (
    A,
    H1,
    Button,
    Div,
    Input,
    Template,
)
from django_compose.base.attributes import disabled, id, style, classes
from django_compose.base.app import Page
from django_compose.base.context import Context, ContextData, DataDict


class TimeData(ContextData):
    time: str | None = None
    in_hours: int | None = None


class CustomButton(Component):

    def build(self, context: Context, children: Children) -> Children:
        time_data = context.get(TimeData) or TimeData()
        return Div[
            "Custom Button Start",
            " ".join(
                [
                    "time in button:",
                    str(time_data.time),
                    "in hours:",
                    str(time_data.in_hours),
                ]
            ),
            Button[children],
            "End of Custom Button",
        ]


class CustomDiv(Component):
    def provide(self, data: DataDict) -> None:
        data.add(TimeData("1:00"))

    def build(self, context: Context, children: Children) -> Children:
        time_data = context.get(TimeData) or TimeData()
        return Div[
            "Custom Div Start ",
            " ".join(
                [
                    "time in div:",
                    str(time_data.time),
                    "in hours:",
                    str(time_data.in_hours),
                ]
            ),
            CustomButton(disabled)[children],
            "Custom Div End",
            Template[Div["This is a template"]],
        ]


class IndexLink(Component):
    def build(self, context: Context, children: Children) -> Children:
        time_data = context.get(TimeData) or TimeData()
        return A(context.router.navigate("index"))[children]


index_page = Page(
    name="index",
    route_pattern="",
    data=[TimeData(time="12:00", in_hours=12)],
    body=lambda context, children: [
        H1((id("header1"), style(color="blue", font_size="12px")))[
            CustomDiv("button", "is-active")["press"],
        ],
        "An Input:",
        Input(classes("input-field"), style(margin="5px"), disabled),
        A(context.router.navigate("service"))["Go to service page"],
    ],
)

service_page = Page(
    name="service",
    body=[
        H1("title", style("font-size:3em"))["Service Page"],
        IndexLink["Go to Index Page"],
    ],
)
