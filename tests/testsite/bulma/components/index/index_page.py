from tymx.base.components import Page

from tymx import bulma
from tymx.base.components.base_components import Provider
import tymx.base.attributes as a
from tymx.base.components.compose_components import PageLink
from tymx.base.modifiers.component_modifiers import NoValidation

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
            PageLink(("button", bulma.radiusless), to="service")["Go to service page"],
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
                "other button"
            ],
            bulma.ProgressBar(bulma.Color.DANGER, size=bulma.Size.SMALL),
        ],
        bulma.Box[
            bulma.Table[
                bulma.TableRow(row_type=bulma.RowType.HEAD)["Num row"],
                [bulma.TableRow[[f"Row {i,j}" for j in range(1, 4)]] for i in range(1, 6)]
            ]
        ],
        bulma.Box[
            bulma.Tags[bulma.Tag["Tag 1"], bulma.Tag["Tag 2"], bulma.Tag["Tag 3"]]
        ]
    ]
]

service_page = Page()[bulma.Content[bulma.Block["Service Page!"],]]
