from django_compose.base.modifiers import SingleTag, ComposedTag


id = SingleTag("id")
classes = ComposedTag("class", lambda values: " ".join(values))
styles = ComposedTag(
    "style",
    lambda values: ";".join(values) + (";" if values else ""),
    lambda k, v: f"{k}:{v}",
)
