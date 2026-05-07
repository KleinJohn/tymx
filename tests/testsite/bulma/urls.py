from django_compose.base.app import DjangoApp
from .components.index.index_page import index_page

app = DjangoApp(
    name="bulma",
    pages=[
        index_page,
    ],
)

app.build()

app_name = app.name
urlpatterns = app.router.get_urlpatterns()
