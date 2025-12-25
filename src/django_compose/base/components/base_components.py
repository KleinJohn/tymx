from __future__ import annotations
from enum import Enum, auto
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
from django_compose.base.context import Consumable, Context, DataDict
from django_compose.base.modifiers.base_modifiers import (
    Modifier,
    Attributes,
    Modifiers,
)

if TYPE_CHECKING:
    from django_compose.base.theme import ComponentTheme


# TYPE DEFINITIONS:


T = TypeVar("T", bound="BaseComponent")
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

ComponentLike: TypeAlias = GenericComponentLike["BaseComponent"]
Children: TypeAlias = GenericComponentChildren["BaseComponent"]

AttributeLike: TypeAlias = str | Attribute | Attributes | Iterable["AttributeLike"]
ModifierLike: TypeAlias = Union[
    str, Attribute, Attributes, Modifier, Modifiers, Iterable["ModifierLike"]
]


default_attribute: Attribute = classes


class BaseComponent(ABC):

    # All Components that allow zero children have to provide an empty constructor.
    def __init__(
        self,
        *attributes: AttributeLike,
        children: Children = None,
        htpy_kwargs: dict[str, str] | None = None,
    ) -> None:
        self.attributes = Attributes()
        self._init_attributes(attributes)
        self._children: list[BaseComponent] = self._children_to_list(children)
        self.htpy_kwargs = htpy_kwargs if htpy_kwargs is not None else {}
        self.provides: DataDict = {}
        if self.attributes:
            self.provides[Attributes] = self.attributes
        self._building = False
        self._do_build = True  # use to prevent recursion in build()

    @abstractmethod
    def build(self, context: Context, children: Children) -> Children:
        raise NotImplementedError()

    @abstractmethod
    def render(self) -> htpy.Node:
        raise NotImplementedError()

    def full_build(self, context: Context) -> ComponentLike:
        self.consume_data(context)
        self._before_build(context)
        children = self._handle_build(context)
        self._after_build(context, children)
        return self._unwrap_component_list(children)

    def update_provider_data(self) -> DataDict:
        return {}

    def consume_data(self, context: Context) -> None:
        attributes = context.get(Attributes)
        if attributes:
            self.attributes.add_all(attributes, overwrite=False)

    def _before_build(self, context: Context) -> None:
        pass

    def _after_build(self, context: Context, components: list[BaseComponent]) -> None:
        pass

    def _before_build_children(
        self, context: Context, children: list[BaseComponent]
    ) -> None:
        self.provides.update(self.update_provider_data())
        context.add_data_frame(self.provides)

    def _after_build_children(
        self, context: Context, children: list[BaseComponent]
    ) -> None:
        context.pop_data_frame()

    def _build_children(
        self, context: Context, children: list[BaseComponent]
    ) -> list[BaseComponent]:
        lst: list[BaseComponent] = []
        self._before_build_children(context, children)
        for child in children:
            lst.extend(self._children_to_list(child.full_build(context)))
        self._after_build_children(context, children)
        return lst

    def _handle_build(self, context: Context) -> list[BaseComponent]:
        children = self._build_children(context, self._children)
        if self._do_build:
            self._building = True
            print(
                self.__class__.__name__,
                [str(frame.data.keys()) for frame in context._data_stack],
            )
            children = self._children_to_list(self.build(context, children))
            self._building = False
        return children

    def _unwrap_component_list(self, components: list[BaseComponent]) -> ComponentLike:
        match len(components):
            case 0:
                return None
            case 1:
                return components[0]
            case _:
                return components

    def _init_attributes(self, attributes: Iterable[AttributeLike]) -> None:
        for attribute in attributes:
            match attribute:
                case str():
                    self.attributes.add(default_attribute(attribute))
                case Attribute():
                    self.attributes.add(attribute)
                case Attributes():
                    self.attributes.add_all(attribute)
                case Iterable():
                    self._init_attributes(attribute)
                case _:
                    raise ValueError(
                        f"Invalid attribute type: {type(attribute)} on {self.__class__.__name__}."
                    )

    def __getitem__(self, children: Children, **kwargs) -> Self:
        copy = self.__class__(
            *self.attributes,
            children=children,
            htpy_kwargs=self.htpy_kwargs,
            **kwargs,
        )
        # break potential build recursion:
        copy._do_build = not self._building
        return copy

    def __class_getitem__(cls, children: Children, **kwargs) -> Self:
        return cls(children=children, **kwargs)

    def __str__(self) -> str:
        if not self._children:
            return self.__class__.__name__
        return f"{self.__class__.__name__}({", ".join(str(child) for child in self._children)})"

    @classmethod
    def _children_to_list(cls, children: Children) -> list[BaseComponent]:
        if not children:
            return []
        match children:
            case type():
                return [children()]
            case str():
                return [Text(text=children)]
            case BaseComponent():
                return [children]
            case Sequence():
                lst: list["BaseComponent"] = []
                for child in children:
                    lst.extend(cls._children_to_list(child))
                return lst
            case Callable():
                return [ContextBuilder(build_function=children)]
            case _:
                raise ValueError("Invalid child type.")


class Component(BaseComponent):

    def __init__(
        self,
        *modifiers: ModifierLike,
        component_theme: ComponentTheme | None = None,
        children: Children = None,
        htpy_kwargs: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            children=children,
            htpy_kwargs=htpy_kwargs,
        )
        self.component_theme = component_theme
        self.modifiers = Modifiers()
        self._init_modifiers(modifiers)
        if self.modifiers:
            self.provides[Modifiers] = self.modifiers

    def _init_modifiers(self, modifiers: Iterable[ModifierLike]) -> None:
        for modifier in modifiers:
            match modifier:
                case str():
                    self.attributes.add(default_attribute(modifier))
                case Attribute():
                    self.attributes.add(modifier)
                case Attributes():
                    self.attributes.add_all(modifier)
                case Modifier():
                    self.modifiers.add(modifier)
                case Modifiers():
                    self.modifiers.add_all(modifier)
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
    def consume_data(self, context: Context) -> None:
        super().consume_data(context)
        modifiers = context.get(Modifiers)
        if modifiers:
            self.modifiers.add_all(self.modifiers, overwrite=False)

    @override
    def _before_build(self, context: Context) -> None:
        """Called before components are built and anything is inherited"""
        super()._before_build(context)
        for modifier in self.modifiers:
            modifier.apply_before_build(context, self)

    @override
    def _after_build(self, context: Context, components: list[BaseComponent]) -> None:
        """Called after components are built and inheritance is handled."""
        super()._after_build(context, components)

        # or in future: context.get(Theme).get_component_theme(self)
        theme = self.component_theme
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
    def __getitem__(self, children: Children, **kwargs) -> Self:
        copy = self.__class__(
            *self.attributes,
            *self.modifiers,
            children=children,
            component_theme=self.component_theme,
            htpy_kwargs=self.htpy_kwargs,
            **kwargs,
        )
        copy._do_build = not self._building
        return copy


class VoidComponentMixin:

    def __getitem__(self, children: Children, **kwargs) -> Self:
        if children:
            raise ValueError(f"{self.__class__.__name__} does not accept any children.")
        return super().__getitem__(children, **kwargs)

    def __class_getitem__(cls, children: Children, **kwargs) -> Self:
        if children:
            raise ValueError(f"{cls.__name__} does not accept any children.")
        return super().__getitem__(children, **kwargs)


class SingleChildComponentMixin:
    def __getitem__(self, children: Children, **kwargs) -> BaseComponent:
        if (
            isinstance(children, Sequence)
            and not isinstance(children, str)
            and len(children) != 1
        ):
            raise ValueError(
                f"{self.__class__.__name__} only accepts exactly one child."
            )
        return super().__getitem__(children, **kwargs)

    def __class_getitem__(cls, children: Children, **kwargs) -> Self:
        if (
            isinstance(children, Sequence)
            and not isinstance(children, str)
            and len(children) != 1
        ):
            raise ValueError(f"{cls.__name__} only accepts exactly one child.")
        return super().__getitem__(children, **kwargs)


class Renderable(ABC):
    @abstractmethod
    def render(self) -> htpy.Renderable: ...


class BuildsItselfMixin:

    def build(
        self: BaseComponent, context: Context, children: Children
    ) -> BaseComponent:
        return self[children]


class ContextBuilder(Component):
    """Calls the given build_function during the build process to generate children."""

    def __init__(
        self,
        *modifiers: ModifierLike,
        build_function: BuildFunctionType,
        component_theme: ComponentTheme | None = None,
        children: Children = None,
        htpy_kwargs: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            *modifiers,
            component_theme=component_theme,
            children=children,
            htpy_kwargs=htpy_kwargs,
        )
        self.build_function = build_function

    @override
    def build(self, context: Context, children: Children) -> Children:
        return self.build_function(context, children)

    @override
    def __getitem__(self, children: Children, **kwargs) -> Self:
        return super().__getitem__(
            children, build_function=self.build_function, **kwargs
        )


@final
class Text(VoidComponentMixin, BuildsItselfMixin, Component):

    def __init__(self, *args, text: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text

    @override
    def render(self) -> str:
        return self.text

    @override
    def __getitem__(self, children: Children, **kwargs) -> Self:
        return super().__getitem__(children, text=self.text, **kwargs)

    @override
    def __str__(self) -> str:
        return f'"{self.text}"'
