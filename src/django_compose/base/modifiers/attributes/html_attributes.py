from django_compose.base.modifiers.attributes import (
    SimpleAttribute,
    ComposedAttribute,
    BooleanAttribute,
)


id = SimpleAttribute("id")
classes = ComposedAttribute("class", lambda values: " ".join(values))
styles = ComposedAttribute(
    "style",
    lambda values: ";".join(values) + (";" if values else ""),
    lambda k, v: f"{k}:{v}",
)
disabled = BooleanAttribute("disabled")


if __name__ == "__main__":
    # Example usage
    id_attr = id("unique-element")
    class_attr = classes("btn", "btn-primary", "active")
    class_attr_empty = classes()
    style_attr = styles(color="red", margin="10px")
    disabled_attr = disabled

    print(str(id_attr))  # Output: id="unique-element"
    print(str(class_attr))  # Output: class="btn btn-primary active"
    print(str(class_attr_empty))  # Output: (empty string)
    print(str(style_attr))  # Output: style="color:red;margin:10px;"
    print(str(disabled_attr))  # Output: disabled
