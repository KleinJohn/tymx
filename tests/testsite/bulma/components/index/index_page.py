from django_compose.base import Page

from django_compose import bulma

dependencies = [bulma.cdn, bulma.fontawesome_cdn]

index_page = Page(
    name="index",
    head=dependencies,
)[
    bulma.Box((bulma.Color.TEXT.shade(50).background))[
        "Hier ein wenig Text",
        bulma.Button(
            icon=bulma.Icon("fa fa-heart"),
        )[
            "Hello, Bulma!",
        ],
    ]
]
