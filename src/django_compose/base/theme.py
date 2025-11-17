from .components import Context, Component, Tag


class ComponentTheme:
    """Apply styling in the form of adding tags or modifying the build method of components.

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

    def modify_tags(self, tags: list[Tag]) -> list[Tag]:
        """Modify the tags of a component.

        Args:
            tags (dict[str, str]): The original tags.

        Returns:
            dict[str, str]: The modified tags.
        """
        return tags


class Theme:
    def __init__(
        self,
        buttonTheme: ComponentTheme | None = None,
    ) -> None:
        self.buttonTheme = buttonTheme or ComponentTheme()
