from django_compose.base.components.html_components import H1, Div, Span
from django_compose.base.modifiers import styles, id, disabled
from django_compose.base.page import Page


if __name__ == "__main__":
    # elem = Div["Test1", Span[Div["Super"]], H1["Header"]]
    page = Page(
        name="index",
        body=[
            H1((id("header1"), styles(color="blue", font_size="12px"), disabled))[
                Div[
                    "Test1",
                    Span[Div["Super"]],
                ],
            ],
        ],
    )
    print(page.render())
