from django_compose.base.components import Component
from django_compose.base.context import Context
from django_compose.base.modifiers import Attributes


class ComponentTheme:
    """Apply styling in the form of adding attributes or modifying the build method of components.

    Themes are distributed inside the context of the build process.
    """

    def modify_build(self, context: Context, component: Component) -> Component:
        """Modify the build process of a component.

        Args:
            context (Context): The build context.
            component (Component): The component to modify.

        Returns:
            Component: The modified component.
        """
        return component

    def modify_attributes(self, attributes: Attributes) -> Attributes:
        """Modify the attributes of a component.

        Args:
            attributes (dict[str, str]): The original attributes.

        Returns:
            dict[str, str]: The modified attributes.
        """
        return attributes


class Theme:
    def __init__(
        self,
        button_theme: ComponentTheme | None = None,
    ) -> None:
        self.button_theme = button_theme or ComponentTheme()
