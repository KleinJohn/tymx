from compose.base import DjangoApp, Page, Div
from compose.base.component_base import H1


home_page = Page(
    name="home",
    body=Div[H1[Div["Hello, World!"]]],
)


app = DjangoApp(starts_on=home_page)
