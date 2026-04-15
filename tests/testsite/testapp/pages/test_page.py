from django_compose.base.components import Component, Children
from django_compose.base.components.compose_components import PageLink
from django_compose.base.components.html_components import (
    A,
    H1,
    Button,
    Div,
    Input,
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
        return lambda context: Div[
            "Custom Div Start",
            Div[
                "time in div: ",
                str(time_data.time),
                " in hours: ",
                str(time_data.in_hours),
            ],
            CustomButton(disabled)[children],
            "Custom Div End",
        ]


index_page = Page(
    name="index",
    route_pattern="",
    data=[TimeData(time="12:00", in_hours=12)],
    head=[],
    body=[
        H1((id("header1"), style(color="blue", font_size="12px")))[
            CustomDiv("button is-active button")["press"],
        ],
        "An Input:",
        Input(classes("input-field"), style(margin="5px"), disabled),
        PageLink(to="service")["Go to Service Page"],
    ],
)

service_page = Page(
    name="service",
    head=[],
    body=[
        H1("title", style="font-size:3em;font-size:3em")["Service Page"],
        PageLink(to="index")["Go to Index Page"],
    ],
)
