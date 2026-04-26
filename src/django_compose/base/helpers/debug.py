from collections.abc import Sequence

from django_compose.base.components import Component


class ValidationError(Exception):
    pass


def validate_is_built(components: Sequence[Component]) -> None:
    for component in components:
        if not component.is_built:
            raise ValidationError(f"{component.__class__.__name__} is not built!")
        validate_is_built(component.children)
