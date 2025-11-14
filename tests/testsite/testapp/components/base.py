from django_compose.base.page import DjangoApp, Page
from django_compose.base.components import Div, H1, P


home_page = Page(
    name="Home Page",
    body=Div[H1["Welcome to the Home Page"], P["This is a sample page."]],
)


app = DjangoApp(starts_on=home_page)


if __name__ == "__main__":
    print(home_page.render())
