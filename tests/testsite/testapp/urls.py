from django_compose.base.page import ComposeApp
from django_compose.django.django_router import to_urlpatterns
from testapp.pages.test_page import index_page


app = ComposeApp(
    starts_on="index",
    pages=[
        index_page,
    ],
)


app_name = "testapp"
urlpatterns = to_urlpatterns(app)
