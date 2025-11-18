from __future__ import annotations
from typing import Iterable, Self, TypeAlias, TypeVar, Union, final, TYPE_CHECKING
from abc import abstractmethod
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

ComponentBaseLike: TypeAlias = GenericComponentLike["ComponentBase"]
ComponentBaseChildren: TypeAlias = GenericComponentChildren["ComponentBase"]
ComponentLike: TypeAlias = GenericComponentLike["Component"]
ComponentChildren: TypeAlias = GenericComponentChildren["Component"]


class Context:
    """Context for building and rendering components.

    The context can hold information that is relevant during the build and render process.
    """

    def __init__(self, theme: Theme) -> None:
        self.theme = theme


class ComponentBase:
    inherit_attributes = True

    # All Components that allow zero children have to provide an empty constructor.
    def __init__(
        self,
        *attributes: Attribute | Iterable[Attribute],
        children: ComponentBaseChildren = None,
        **htpy_kwargs: str,
    ) -> None:
        attr_list: list[Attribute] = []
        for attribute in attributes:
            if isinstance(attribute, Iterable):
                attr_list.extend(attribute)
            else:
                attr_list.append(attribute)
        self.attributes = Attributes(*attr_list)
        self.children: tuple["ComponentBase", ...] = (
            ComponentBase._fill_component_base_children(children)
        )
        self._htpy_kwargs: dict[str, str] = htpy_kwargs

    def __getitem__(self, children: ComponentBaseChildren) -> ComponentBase:
        return self.__class__(
            *self.attributes,
            children=ComponentBase._fill_component_base_children(children),
            **self._htpy_kwargs,
        )

    def __class_getitem__(cls, children: ComponentBaseChildren) -> Self:
        return cls(
            children=cls._fill_component_base_children(children),
        )

    def __str__(self) -> str:
        if not self.children:
            return self.__class__.__name__
        return f"{self.__class__.__name__}({", ".join(str(child) for child in self.children)})"

    @abstractmethod
    def build(
        self, context: Context, children: ComponentBaseChildren
    ) -> ComponentBaseChildren:
        raise NotImplementedError()

    @abstractmethod
    def render(self) -> htpy.Node:
        raise NotImplementedError()

    def full_build(self, context: Context) -> tuple["ComponentBase", ...]:
        children = (child.full_build(context) for child in self.children)
        self_built = self.build(context, children)
        components = ComponentBase._fill_component_base_children(self_built)
        if self.__class__.inherit_attributes:
            for component in components:
                component.attributes.add_all(self.attributes)
        return components

    @classmethod
    def _fill_component_base_children(
        cls,
        children: ComponentBaseChildren,
    ) -> tuple["ComponentBase", ...]:
        if not children:
            return tuple()
        match children:
            case type():
                return (children(),)
            case str():
                return (Text(children),)
            case ComponentBase():
                return (children,)
            case _:
                lst: list["ComponentBase"] = []
                for child in children:
                    lst.extend(cls._fill_component_base_children(child))
                return tuple(lst)


class Component(ComponentBase):

    def __init__(
        self,
        *attributes: Attribute | Iterable[Attribute],
        modifiers: Iterable[Modifier] | None = None,
        theme: ComponentTheme | None = None,
        children: ComponentBaseChildren = None,
        **htpy_kwargs: str,
    ) -> None:
        super().__init__(*attributes, children=children, **htpy_kwargs)
        self.theme = theme
        self.modifiers: list[Modifier] = list(modifiers or [])

    @abstractmethod
    def build(
        self, context: Context, children: ComponentBaseChildren
    ) -> ComponentChildren:
        raise NotImplementedError()

    def render(self) -> htpy.Node:
        raise NotImplementedError(
            "Render method not implemented. "
            "- Most likely called render on an unbuilt component. "
            "Make sure your component builds down to html components."
        )

    def full_build(self, context: Context) -> tuple["Component", ...]:
        children = (child.full_build(context) for child in self.children)
        built_self = self.build(context, children)
        components = Component._fill_component_children(built_self)
        comp_list: list[Component] = []
        for component in components:
            c = self.apply_theme(context, component)
            c = self.apply_modifiers(context, c)
            comp_list.append(c)
        return tuple(comp_list)

    def apply_theme(self, context: Context, component: "Component") -> "Component":
        if self.theme:
            component = self.theme.modify_build(context, component)
            if self.__class__.inherit_attributes:
                component.attributes.add_all(self.attributes)
            component.attributes = self.theme.modify_attributes(component.attributes)
        return component

    def apply_modifiers(self, context: Context, component: "Component") -> "Component":
        for modifier in self.modifiers:
            component = modifier.apply(context, component)
        return component

    def __getitem__(self, children: ComponentBaseChildren) -> Self:
        return self.__class__(
            *self.attributes,
            modifiers=self.modifiers,
            children=self.__class__._fill_component_base_children(children),
            theme=self.theme,
            **self._htpy_kwargs,
        )

    @classmethod
    def _fill_component_children(
        cls,
        children: ComponentChildren,
    ) -> tuple["Component", ...]:
        if not children:
            return tuple()
        match children:
            case type():
                return (children(),)
            case str():
                return (Text(children),)
            case ComponentBase():
                return (children,)
            case _:
                lst: list["Component"] = []
                for child in children:
                    lst.extend(cls._fill_component_children(child))
                return tuple(lst)


class VoidComponentMixin:
    pass


class SingleChildComponentMixin:
    pass


@final
class Text(VoidComponentMixin, Component):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def build(self, context: Context, children: ComponentBaseChildren) -> "Component":
        return Text(self.text)

    def render(self) -> htpy.Node:
        return self.text

    def __str__(self) -> str:
        return f'"{self.text}"'


class ThemedComponent(Component):

    @abstractmethod
    def get_theme(self, theme: Theme) -> ComponentTheme | None:
        raise NotImplementedError()

    def apply_theme(self, context: Context, component: "Component") -> "Component":
        context_theme = self.get_theme(context.theme)
        if self.theme:
            component = self.theme.modify_build(context, component)
            component.attributes = self.theme.modify_attributes(component.attributes)
        elif context_theme:
            component = context_theme.modify_build(context, component)
            component.attributes = context_theme.modify_attributes(component.attributes)
        return component
