from django_compose.base.app import ComposeApp
from testapp.pages.test_page import index_page


app = ComposeApp(
    starts_on="index",
    pages=[
        index_page,
    ],
)

app.build()

app_name = "testapp"
urlpatterns = app.router.get_urlpatterns()
