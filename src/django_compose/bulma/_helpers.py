import django_compose.base.components.html_components as html
import django_compose.base.attributes as a

cdn = html.Link(
    (
        a.rel("stylesheet"),
        a.href("https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css"),
    )
)


fontawesome_cdn = html.Link(
    (
        a.rel("stylesheet"),
        a.href(
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
        ),
    )
)
