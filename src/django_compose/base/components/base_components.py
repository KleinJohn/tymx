from __future__ import annotations
from enum import Enum
from typing import (
    Self,
    TypeAlias,
    TypeVar,
    Union,
    final,
    TYPE_CHECKING,
    override,
)
from collections.abc import Callable, Sequence, Iterable
from abc import ABC, abstractmethod
import htpy

from django_compose.base.attributes import Attribute, classes
from django_compose.base.context import Context
from django_compose.base.modifiers.base_modifiers import Modifier, Attributes

if TYPE_CHECKING:
    from django_compose.base.theme import ComponentTheme


# TYPE DEFINITIONS:


T = TypeVar("T", bound="ComponentBase")
GenericComponentLike: TypeAlias = Union[None, T, list[T]]
# prevent nesting of build functions:
GenericComponentChildrenNoLambda: TypeAlias = Union[
    None,
    str,
    T,
    type[T],
    Sequence["GenericComponentChildrenNoLambda[T]"],
]
BuildFunctionType: TypeAlias = Callable[[Context, "Children"], "Children"]
GenericComponentChildren: TypeAlias = Union[
    GenericComponentChildrenNoLambda[T],
    BuildFunctionType,
]

ComponentLike: TypeAlias = GenericComponentLike["ComponentBase"]
Children: TypeAlias = GenericComponentChildren["ComponentBase"]

AttributeLike: TypeAlias = str | Attribute | Iterable["AttributeLike"]
ModifierLike: TypeAlias = Union[str, Attribute, "Modifier", Iterable["ModifierLike"]]


default_attribute: Attribute = classes


class ComponentPolicy(Enum):

    NONE = 1
    "No inheritance."

    COMPONENTS = 2
    "Inherit to top-level components in build method."

    CHILDREN = 3
    "Exclude components in the build function from inheritance."


class ComponentBase(ABC):
    inheritance_policy = ComponentPolicy.COMPONENTS
    build_policy = ComponentPolicy.COMPONENTS

    # All Components that allow zero children have to provide an empty constructor.
    def __init__(
        self,
        *attributes: AttributeLike,
        children: Children = None,
        inheritance_policy: ComponentPolicy | None = None,
        build_policy: ComponentPolicy | None = None,
        **htpy_kwargs: str,
    ) -> None:
        self.attributes = Attributes()
        self._init_attributes(attributes)
        self.children: list[ComponentBase] = self._children_to_list(children)
        self.inheritance_policy = (
            inheritance_policy or self.__class__.inheritance_policy
        )
        self.build_policy = build_policy or self.__class__.build_policy
        self._htpy_kwargs = htpy_kwargs

    def _init_attributes(self, attributes: Iterable[AttributeLike]) -> None:
        for attribute in attributes:
            match attribute:
                case str():
                    self.attributes.add(default_attribute(attribute))
                case Attribute():
                    self.attributes.add(attribute)
                case Iterable():
                    self._init_attributes(attribute)
                case _:
                    raise ValueError("Invalid attribute type.")

    def __getitem__(self, children: Children) -> Self:
        return self.__class__(
            *self.attributes,
            children=children,
            inheritance_policy=self.inheritance_policy,
            build_policy=self.build_policy,
            **self._htpy_kwargs,
        )

    def __class_getitem__(cls, children: Children) -> Self:
        return cls(children=children)

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

    def full_build(self, context: Context) -> ComponentLike:
        self._before_build(context)
        components = self._handle_build(context)
        self._handle_inheritance(context, components)
        self._after_build(context, components)
        return self._unwrap_component_list(components)

    def _before_build(self, context: Context) -> None:
        """Called before components are built and anything is inherited"""
        pass

    def _after_build(self, context: Context, components: list[ComponentBase]) -> None:
        """Called after components are built and inheritance is handled."""
        pass

    def _handle_inheritance(
        self, context: Context, components: list[ComponentBase]
    ) -> None:
        if self.inheritance_policy == ComponentPolicy.COMPONENTS:
            for component in components:
                self._inherit_to_component(context, component)
        elif self.inheritance_policy == ComponentPolicy.CHILDREN:
            for component in self.children:
                self._inherit_to_component(context, component)

    def _inherit_to_component(self, context: Context, component: ComponentBase) -> None:
        component.attributes.add_all(self.attributes)

    def _handle_build(self, context: Context) -> list[ComponentBase]:
        lst: list[ComponentBase] = []
        children = self.children

        if self.build_policy == ComponentPolicy.CHILDREN:
            for child in self.children:
                lst.extend(self._children_to_list(child.full_build(context)))
            children = lst
        components = self._children_to_list(self.build(context, children))
        if self.build_policy == ComponentPolicy.COMPONENTS:
            for component in components:
                lst.extend(self._children_to_list(component.full_build(context)))
            components = lst
        return components

    def _unwrap_component_list(self, components: list[ComponentBase]) -> ComponentLike:
        match len(components):
            case 0:
                return None
            case 1:
                return components[0]
            case _:
                return components

    @classmethod
    def _children_to_list(cls, children: Children) -> list[ComponentBase]:
        if not children:
            return []
        match children:
            case type():
                return [children()]
            case str():
                return [Text(children)]
            case ComponentBase():
                return [children]
            case Sequence():
                lst: list["ComponentBase"] = []
                for child in children:
                    lst.extend(cls._children_to_list(child))
                return lst
            case Callable():
                return [ContextBuilder(build_function=children)]
            case _:
                raise ValueError("Invalid child type.")


class Component(ComponentBase):

    def __init__(
        self,
        *modifiers: ModifierLike,
        theme: ComponentTheme | None = None,
        children: Children = None,
        inheritance_policy: ComponentPolicy | None = None,
        build_policy: ComponentPolicy | None = None,
        **htpy_kwargs: str,
    ) -> None:
        super().__init__(
            children=children,
            inheritance_policy=inheritance_policy,
            build_policy=build_policy,
            **htpy_kwargs,
        )
        self.theme = theme
        self.modifiers: list[Modifier] = []
        self._init_modifiers(modifiers)

    def _init_modifiers(self, modifiers: Iterable[ModifierLike]) -> None:
        for modifier in modifiers:
            match modifier:
                case str():
                    self.attributes.add(default_attribute(modifier))
                case Attribute():
                    self.attributes.add(modifier)
                case Modifier():
                    self.modifiers.append(modifier)
                case Iterable():
                    self._init_modifiers(modifier)
                case _:
                    raise ValueError("Invalid modifier type.")

    @abstractmethod
    def build(self, context: Context, children: Children) -> Children:
        raise NotImplementedError()

    @override
    def render(self) -> htpy.Node:
        # Can omit render method if build method returns other components.
        raise NotImplementedError(
            "Render method not implemented. "
            "- Most likely called render on an unbuilt component. "
            "Make sure your components build down to html."
        )

    @override
    def _before_build(self, context: Context) -> None:
        """Called before components are built and anything is inherited"""
        super()._before_build(context)
        for modifier in self.modifiers:
            modifier.apply_before_build(context, self)

    @override
    def _after_build(self, context: Context, components: list[ComponentBase]) -> None:
        """Called after components are built and inheritance is handled."""
        super()._after_build(context, components)

        theme = self.theme  # or in future: context.theme.get_component_theme(self)
        for i, component in enumerate(components):
            if not isinstance(component, Component):
                continue
            if theme:
                component = theme.modify_build(context, component)
                component.attributes = theme.modify_attributes(component.attributes)
            for modifier in self.modifiers:
                component = modifier.apply(context, component)
            components[i] = component

    @override
    def __getitem__(self, children: Children) -> Self:
        return self.__class__(
            *self.attributes,
            *self.modifiers,
            children=children,
            theme=self.theme,
            inheritance_policy=self.inheritance_policy,
            build_policy=self.build_policy,
            **self._htpy_kwargs,
        )


class VoidComponentMixin:
    inheritance_policy = ComponentPolicy.NONE
    build_policy = ComponentPolicy.NONE

    def __getitem__(self, children: Children) -> ComponentBase:
        if children:
            raise ValueError(f"{self.__class__.__name__} does not accept any children.")
        return super().__getitem__(children)  # type: ignore

    def __class_getitem__(cls, children: Children) -> Self:
        if children:
            raise ValueError(f"{cls.__name__} does not accept any children.")
        return super().__getitem__(children)  # type: ignore


class SingleChildComponentMixin:
    def __getitem__(self, children: Children) -> ComponentBase:
        if (
            isinstance(children, Sequence)
            and not isinstance(children, str)
            and len(children) != 1
        ):
            raise ValueError(
                f"{self.__class__.__name__} only accepts exactly one child."
            )
        return super().__getitem__(children)  # type: ignore

    def __class_getitem__(cls, children: Children) -> Self:
        if (
            isinstance(children, Sequence)
            and not isinstance(children, str)
            and len(children) != 1
        ):
            raise ValueError(f"{cls.__name__} only accepts exactly one child.")
        return super().__getitem__(children)  # type: ignore


class RenderableComponentMixin:
    build_policy = ComponentPolicy.CHILDREN
    inheritance_policy = ComponentPolicy.CHILDREN

    def build(
        self: ComponentBase, context: Context, children: Children
    ) -> ComponentBase:
        return self[children]


class ContextBuilder(Component):
    """Calls the given build_function during the build process to generate children."""

    def __init__(
        self,
        *modifiers: ModifierLike,
        build_function: BuildFunctionType,
        theme: ComponentTheme | None = None,
        children: Children = None,
        inheritance_policy: ComponentPolicy | None = None,
        build_policy: ComponentPolicy | None = None,
        **htpy_kwargs: str,
    ) -> None:
        super().__init__(
            *modifiers,
            theme=theme,
            children=children,
            inheritance_policy=inheritance_policy,
            build_policy=build_policy,
            **htpy_kwargs,
        )
        self.build_function = build_function

    @override
    def build(self, context: Context, children: Children) -> Children:
        return self.build_function(context, children)


@final
class Text(VoidComponentMixin, Component):

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    @override
    def full_build(self, context: Context) -> "Text":
        return Text(self.text)

    @override
    def build(self, context: Context, children: Children) -> "Component":
        return Text(self.text)

    @override
    def render(self) -> str:
        return self.text

    @override
    def __str__(self) -> str:
        return f'"{self.text}"'
