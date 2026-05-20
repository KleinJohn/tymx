from tymx.django import App
from testapp.pages.test_page import index_page

app = App(
    name="testapp",
    pages={
        "index": index_page,
    },
)

app.build()

app_name = app.name
urlpatterns = app.router.get_urlpatterns()
