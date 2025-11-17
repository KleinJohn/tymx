from django_compose.base.modifiers import (
    SingleAttribute,
    ComposedAttribute,
    BooleanAttribute,
)


id = SingleAttribute("id")
classes = ComposedAttribute("class", lambda values: " ".join(values))
styles = ComposedAttribute(
    "style",
    lambda values: ";".join(values) + (";" if values else ""),
    lambda k, v: f"{k}:{v}",
)
disabled = BooleanAttribute("disabled")
