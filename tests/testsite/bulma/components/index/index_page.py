from tymx.base.components import Page

from tymx import bulma
from tymx.base.components.base_components import Provider
import tymx.base.attributes as a
from tymx.base.components.compose_components import PageLink

dependencies = [bulma.cdn, bulma.fontawesome_cdn]

index_page = Page(head=dependencies)[
    Provider(provides=a.Attributes(a.classes("my-provider")))[
        bulma.Box(
            (
                bulma.Text.size(mobile=6, tablet=5, desktop=4).centered,
                bulma.Flex.justify_center.align_items_center.wrap,
            )
        )[
            bulma.Block((bulma.Flex.align_self_baseline.grow(3),))[
                "Hier ein wenig Text"
            ],
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
                PageLink(to="service")["Go to service page"],
            ],
            bulma.ProgressBar(bulma.Color.DANGER, size=bulma.Size.SMALL),
        ]
    ]
]

service_page = Page()[bulma.Content[bulma.Block["Service Page!"],]]
