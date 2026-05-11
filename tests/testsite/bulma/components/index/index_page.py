from django_compose.base import Page

from django_compose import bulma

dependencies = [bulma.cdn, bulma.fontawesome_cdn]

index_page = Page(
    name="index",
    head=dependencies,
)[
    bulma.Box(
        (
            bulma.Text.size(mobile=6, tablet=5, desktop=4).centered,
            bulma.Display.hide(mobile=True, tablet=True, desktop=True),
        )
    )[
        "Hier ein wenig Text",
        bulma.Button(
            (
                bulma.M.all(2),
                bulma.P.x2,
                bulma.Color.DANGER.text.invert,
                bulma.Color.DANGER.background,
            ),
            icon=bulma.Icon("fa fa-rocket"),
            icon_side=bulma.Side.RIGHT,
        )[
            "Hello, Bulma!",
        ],
    ]
]
