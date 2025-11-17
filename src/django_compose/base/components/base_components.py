from __future__ import annotations
from typing import Iterable, Self, TypeAlias, Union, final, TYPE_CHECKING
from abc import ABCMeta, abstractmethod
import htpy

from django_compose.base.modifiers import Attributes, Attribute
from django_compose.base.modifiers.base_modifiers import Modifier

if TYPE_CHECKING:
    from django_compose.base.theme import Theme, ComponentTheme


ComponentBaseLike: TypeAlias = Union["ComponentBase", type["ComponentBase"], str]
ComponentBaseChildren: TypeAlias = Union[
    None, ComponentBaseLike, Iterable[ComponentBaseLike]
]
ComponentLike: TypeAlias = Union["Component", type["Component"], str]
ComponentChildren: TypeAlias = Union[None, ComponentLike, Iterable[ComponentLike]]


class Context:
    """Context for building and rendering components.

    The context can hold information that is relevant during the build and render process.
    """

    def __init__(self, theme: Theme) -> None:
        self.theme = theme


def _component_validate_child(child: ComponentBaseLike) -> "ComponentBase":
    if isinstance(child, type):
        return child()
    elif isinstance(child, str):
        return Text(child)
    return child


def _fill_component_children(
    children: ComponentBaseChildren,
) -> tuple["ComponentBase", ...]:
    if not children:
        return tuple()
    if isinstance(children, Iterable) and not isinstance(children, str):
        return tuple(map(_component_validate_child, children))
    else:
        return (_component_validate_child(children),)


class ComponentBaseMeta(type):

    def __getitem__(cls, children: ComponentBaseChildren) -> "ComponentBase":
        return cls(children=children)

    def __str__(cls) -> str:
        return cls.__name__


class AbstractComponentBaseMeta(ABCMeta, ComponentBaseMeta):
    pass


class AbstractComponentMeta(AbstractComponentBaseMeta):
    def __getitem__(cls, children: ComponentBaseChildren) -> "Component":
        return cls(children=children)


class ComponentBase(metaclass=AbstractComponentBaseMeta):
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
        self.children: tuple["ComponentBase", ...] = _fill_component_children(children)
        self._htpy_kwargs: dict[str, str] = htpy_kwargs

    def __getitem__(self, children: ComponentBaseChildren) -> Self:
        return self.__class__(
            *self.attributes,
            children=_fill_component_children(children),
            **self._htpy_kwargs,
        )

    def __str__(self) -> str:
        if not self.children:
            return self.__class__.__name__
        return f"{self.__class__.__name__}({", ".join(str(child) for child in self.children)})"

    @abstractmethod
    def build(
        self, context: Context, children: ComponentBaseChildren
    ) -> "ComponentBase":
        raise NotImplementedError()

    @abstractmethod
    def render(self) -> htpy.Node:
        raise NotImplementedError()

    def full_build(self, context: Context) -> "ComponentBase":
        self_built = self.build(context, self.children)
        if self.__class__.inherit_attributes:
            self_built.attributes.add_all(self.attributes)
        return self_built


class Component(ComponentBase, metaclass=AbstractComponentMeta):

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
    def build(self, context: Context, children: ComponentBaseChildren) -> "Component":
        raise NotImplementedError()

    def render(self) -> htpy.Node:
        raise NotImplementedError(
            "Render method not implemented. "
            "- Most likely called render on an unbuilt component. "
            "Make sure your component builds down to html components."
        )

    def full_build(self, context: Context) -> "Component":
        children = (child.full_build(context) for child in self.children)
        built_self = self.build(context, children)
        built_self = self.apply_theme(context, built_self)
        built_self = self.apply_modifiers(context, built_self)
        return built_self

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
            children=_fill_component_children(children),
            theme=self.theme,
            **self._htpy_kwargs,
        )


class AbstractLeafComponentMeta(AbstractComponentMeta):
    def __getitem__(cls, children: ComponentBaseChildren) -> "LeafComponent":
        if children:
            raise ValueError(
                f"{cls.__name__} does not accept any children, got {children}"
            )
        return cls()


class LeafComponent(Component, metaclass=AbstractLeafComponentMeta):
    def __getitem__(self, children: ComponentBaseChildren) -> "LeafComponent":
        if children:
            raise ValueError(
                f"{self.__class__.__name__} does not accept any children, got {children}"
            )
        return super().__getitem__(children)

    @abstractmethod
    def build(self, context: Context, children: ComponentBaseChildren) -> "Component":
        raise NotImplementedError()


class AbstractSingleChildComponentMeta(AbstractComponentMeta):
    def __getitem__(cls, children: ComponentBaseChildren) -> "SingleChildComponent":
        if (
            isinstance(children, tuple)
            and not isinstance(children, str)
            and len(children) != 1
        ):
            raise ValueError(
                f"{cls.__name__} only accepts a single child, got {len(children)}"
            )
        return cls(children=children)


class SingleChildComponent(Component, metaclass=AbstractSingleChildComponentMeta):
    @property
    def child(self) -> ComponentBase:
        return self.children[0]

    def __getitem__(self, children: ComponentBaseChildren) -> "SingleChildComponent":
        if (
            isinstance(children, tuple)
            and not isinstance(children, str)
            and len(children) != 1
        ):
            raise ValueError(
                f"{self.__class__.__name__} only accepts a single child, got {len(children)}"
            )
        return super().__getitem__(children)

    @abstractmethod
    def build(self, context: Context, children: ComponentBaseChildren) -> "Component":
        raise NotImplementedError()


class AbstractTextComponentMeta(AbstractLeafComponentMeta):
    def __getitem__(cls, children: ComponentBaseChildren) -> "Text":
        if isinstance(children, str):
            return Text(children)
        raise ValueError(
            f"{cls.__name__} only accepts a single string child, got {children}"
        )


@final
class Text(LeafComponent, metaclass=AbstractTextComponentMeta):
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
