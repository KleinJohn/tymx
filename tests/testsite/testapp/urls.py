from django_compose.base.app import DjangoApp
from testapp.pages.test_page import index_page

app = DjangoApp(
    name="testapp",
    pages=[
        index_page,
    ],
)

app.build()

app_name = app.name
urlpatterns = app.router.get_urlpatterns()
