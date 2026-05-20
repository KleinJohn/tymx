from tymx.django import App
from .components.index.index_page import index_page

app = App(
    name="bulma",
    pages=[
        index_page,
    ],
)

app.build()

app_name = app.name
urlpatterns = app.router.get_urlpatterns()
