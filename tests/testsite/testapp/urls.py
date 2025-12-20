from django_compose.base.app import ComposeApp
from testapp.pages.test_page import index_page, service_page


app = ComposeApp(
    name="testapp",
    starts_on="index",
    pages=[
        index_page,
        service_page,
    ],
)

app.build()

app_name = app.name
urlpatterns = app.router.get_urlpatterns()
