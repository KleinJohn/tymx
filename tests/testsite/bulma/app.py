from tymx.django import App
from .components.index.index_page import index_page, service_page

bulma_app = App(
    name="bulma",
    pages={
        "index": index_page,
        "service": service_page,
    },
)
