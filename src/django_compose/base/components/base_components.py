from __future__ import annotations
from typing import (
    Iterable,
    Self,
    TypeAlias,
    TypeVar,
    Union,
    final,
    TYPE_CHECKING,
)
from abc import ABC, abstractmethod
import htpy

from django_compose.base.modifiers import Attributes, Attribute
from django_compose.base.modifiers.base_modifiers import Modifier

if TYPE_CHECKING:
    from django_compose.base.theme import Theme, ComponentTheme

T = TypeVar("T", bound="ComponentBase")
GenericComponentLike: TypeAlias = Union[T, type[T], str]
GenericComponentChildren: TypeAlias = Union[
    None, GenericComponentLike[T], Iterable["GenericComponentChildren[T]"]
]

ComponentLike: TypeAlias = GenericComponentLike["ComponentBase"]
Children: TypeAlias = GenericComponentChildren["ComponentBase"]


class Context:
    """Context for building and rendering components.

    The context can hold information that is relevant during the build and render process.
    """

    def __init__(self, theme: Theme) -> None:
        self.theme = theme


class ComponentBase(ABC):
    inherit_attributes = True

    # All Components that allow zero children have to provide an empty constructor.
    def __init__(
        self,
        *attributes: Attribute | Iterable[Attribute],
        children: Children = None,
        **htpy_kwargs: str,
    ) -> None:
        attr_list: list[Attribute] = []
        for attribute in attributes:
            if isinstance(attribute, Iterable):
                attr_list.extend(attribute)
            else:
                attr_list.append(attribute)
        self.attributes = Attributes(*attr_list)
        self.children: list[ComponentBase] = ComponentBase._children_base_to_list(
            children
        )
        self._htpy_kwargs = htpy_kwargs

    def __getitem__(self, children: Children) -> ComponentBase:
        return self.__class__(
            *self.attributes,
            children=ComponentBase._children_base_to_list(children),
            **self._htpy_kwargs,
        )

    def __class_getitem__(cls, children: Children) -> Self:
        return cls(children=cls._children_base_to_list(children))

    def __str__(self) -> str:
        if not self.children:
            return self.__class__.__name__
        return f"{self.__class__.__name__}({", ".join(str(child) for child in self.children)})"

    @abstractmethod
    def build(self, context: Context, children: Children) -> Children:
        raise NotImplementedError()

    @abstractmethod
    def render(self) -> htpy.Node:
        raise NotImplementedError()

    def full_build(self, context: Context) -> ComponentBase:
        self_built = self.build(context, self.children)
        attributes = self.attributes if self.__class__.inherit_attributes else ()
        builder = ComponentBuilder(
            *attributes,
            children=self_built,
            theme=None,
            modifiers=None,
            **self._htpy_kwargs,
        )
        return builder.full_build(context)

    def _build_children(self, context: Context) -> None:
        """Only call this on already built components, since it modifies self.children in place."""
        for i in range(len(self.children)):
            self.children[i] = self.children[i].full_build(context)

    @classmethod
    def _children_base_to_list(
        cls,
        children: Children,
    ) -> list[ComponentBase]:
        if not children:
            return []
        match children:
            case type():
                return [children()]
            case str():
                return [Text(children)]
            case ComponentBase():
                return [children]
            case _:
                lst: list["ComponentBase"] = []
                for child in children:
                    lst.extend(cls._children_base_to_list(child))
                return lst


class Component(ComponentBase):
    inherit_attributes = True
    inherit_modifiers = True
    inherit_theme = True

    def __init__(
        self,
        *attributes: Attribute | Iterable[Attribute],
        modifiers: Iterable[Modifier] | None = None,
        theme: ComponentTheme | None = None,
        children: Children = None,
        **htpy_kwargs: str,
    ) -> None:
        super().__init__(*attributes, children=children, **htpy_kwargs)
        self.theme = theme
        self.modifiers: list[Modifier] = list(modifiers or [])

    @abstractmethod
    def build(self, context: Context, children: Children) -> Children:
        raise NotImplementedError()

    def render(self) -> htpy.Node:
        raise NotImplementedError(
            "Render method not implemented. "
            "- Most likely called render on an unbuilt component. "
            "Make sure your components build down to html."
        )

    def full_build(self, context: Context) -> Component:
        built_self = self.build(context, self.children)
        builder: Component = self._create_component_builder(built_self)
        builder.full_build(context)
        return builder

    def apply_theme_to_children(
        self, context: Context, theme: ComponentTheme | None
    ) -> None:
        for i, _ in enumerate(self.children):
            if theme:
                self.children[i] = theme.modify_build(context, self.children[i])
            if self.__class__.inherit_attributes:
                self.children[i].attributes.add_all(self.attributes)
            if theme:
                self.children[i].attributes = theme.modify_attributes(
                    self.children[i].attributes
                )

    def __getitem__(self, children: Children) -> Self:
        return self.__class__(
            *self.attributes,
            modifiers=self.modifiers,
            children=self.__class__._children_base_to_list(children),
            theme=self.theme,
            **self._htpy_kwargs,
        )

    def _create_component_builder(self, children: Children) -> ComponentBuilder:
        attributes = self.attributes if self.__class__.inherit_attributes else ()
        modifiers = self.modifiers if self.__class__.inherit_modifiers else ()
        theme = self.theme if self.__class__.inherit_theme else None
        return ComponentBuilder(
            *attributes,
            children=children,
            modifiers=modifiers,
            theme=theme,
        )

    @classmethod
    def _children_to_list(
        cls,
        children: GenericComponentChildren["Component"],
    ) -> list["Component"]:
        if not children:
            return []
        match children:
            case type():
                return [children()]
            case str():
                return [Text(children)]
            case ComponentBase():
                return [children]
            case _:
                lst: list["Component"] = []
                for child in children:
                    lst.extend(cls._children_to_list(child))
                return lst


@final
class ComponentBuilder(Component):
    # Don't need to set inherit variables, since ComponentBuilder always inherits everything.

    def __str__(self) -> str:
        return ", ".join(str(child) for child in self.children)

    def full_build(self, context: Context) -> Component:
        builder: Component = self
        for modifier in self.modifiers:
            builder = modifier.apply_before_build(context, builder)

        builder._build_children(context)
        builder.apply_theme_to_children(context, self.theme)

        for modifier in self.modifiers:
            builder = modifier.apply_after_build(context, builder)
        return builder

    def build(self, context: Context, children: Children) -> Children:
        return children

    def render(self) -> htpy.Node:
        return (child.render() for child in self.children)


class VoidComponentMixin:
    pass


class SingleChildComponentMixin:
    pass


@final
class Text(VoidComponentMixin, Component):
    inherit_attributes = False

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def full_build(self, context: Context) -> "Text":
        return Text(self.text)

    def build(self, context: Context, children: Children) -> "Component":
        return Text(self.text)

    def render(self) -> htpy.Node:
        return self.text

    def __str__(self) -> str:
        return f'"{self.text}"'


class ThemedComponent(Component):

    @abstractmethod
    def get_theme(self, theme: Theme) -> ComponentTheme | None:
        raise NotImplementedError()

    def apply_theme_to_children(
        self, context: Context, theme: ComponentTheme | None
    ) -> None:
        return super().apply_theme_to_children(
            context, theme or self.get_theme(context.theme)
        )
