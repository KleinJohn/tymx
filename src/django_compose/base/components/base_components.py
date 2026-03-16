from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Sequence
from typing import TYPE_CHECKING, TypeAlias

from typing_extensions import (
    Any,
    Self,
    TypeVar,
    final,
    override,
)

from django_compose.base.attributes import Attribute, classes, ALL_ATTRIBUTES
from django_compose.base.context import Context, ContextFrame, DataDict
from django_compose.base.modifiers.base_modifiers import (
    Attributes,
    Modifier,
    Modifiers,
)

if TYPE_CHECKING:
    import htpy

    from django_compose.base.theme import ComponentTheme


# TYPE DEFINITIONS:


T = TypeVar("T", bound="BaseComponent")
GenericComponentLike: TypeAlias = None | T | list[T]
TemplateFunctionType: TypeAlias = Callable[[Context], "Children"]
GenericComponentChildren: TypeAlias = (
    None
    | str
    | T
    | type[T]
    | TemplateFunctionType
    | Sequence["GenericComponentChildren[T]"]
)

ComponentLike: TypeAlias = GenericComponentLike["BaseComponent"]
Children: TypeAlias = GenericComponentChildren["BaseComponent"]

AttributeLike: TypeAlias = str | Attribute | Attributes | Iterable["AttributeLike"]
ModifierLike: TypeAlias = (
    str | Attribute | Attributes | Modifier | Modifiers | Iterable["ModifierLike"]
)


class BaseComponent(ABC):
    # inherit_properties: set[type] = {Attributes}

    # All Components that allow zero children have to provide an empty constructor.
    def __init__(
        self,
        *attributes: AttributeLike,
        children: Children = None,
        htpy_kwargs: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        self._attributes = Attributes()
        self._init_attributes(attributes)
        self._children: list[BaseComponent] = self._children_to_list(children)
        self._htpy_kwargs = htpy_kwargs if htpy_kwargs is not None else {}
        self._building = False
        self._build_data: ContextFrame = ContextFrame(self)
        self._build_context: Context | None = None
        self._is_built = False  # use to prevent recursion in build()
        self.kwargs: dict[str, Any] = dict(kwargs)
        self.props: dict[str, Any] = {}
        self._extract_attributes_from_kwargs(**self.kwargs)

    @property
    def attributes(self) -> Attributes:
        if self.is_built:
            return self._attributes
        return self._build_data.get(Attributes) or Attributes()

    @attributes.setter
    def attributes(self, value: Attributes) -> None:
        if self.is_built:
            self._attributes = value
        self._build_data[Attributes] = value

    @property
    def context(self) -> Context:
        if self._build_context is None:
            raise ValueError("Component is not being built, no context available.")
        self._build_context.current_component = self
        return self._build_context

    @context.setter
    def context(self, value: Context | None) -> None:
        self._build_context = value

    @property
    def is_built(self) -> bool:
        return self._is_built

    @abstractmethod
    def build(self, context: Context, children: Children) -> Children:
        raise NotImplementedError()

    @abstractmethod
    def render(self) -> htpy.Node:
        raise NotImplementedError()

    def use_props(self, **props: Any) -> None:
        """Declare that the component uses the given props in its build method.
        
        This is used to make sure that props are properly cloned when using the
        component multiple times by __getitem__.
        """
        self.props.update(props)

    def provide(self, data: DataDict) -> None:
        if self._attributes and not self.is_built:
            data[Attributes] = self._attributes

    def consume(self) -> None:
        inherited_attributes = self.context.get(Attributes) or Attributes()
        self.attributes = inherited_attributes | self._attributes

    def full_build(self, context: Context) -> ComponentLike:
        """The component should return to its original state after building."""
        self._prepare_build(context)
        self.consume()
        self._before_build()
        children = self._handle_build()
        self._after_build(children)
        self._finish_build()
        return self._unwrap_component_list(children)

    def _handle_build(self) -> list[BaseComponent]:
        children = self._children
        if not self.is_built:
            self._building = True
            children = self._children_to_list(self.build(self.context, self._children))
            self._building = False

        self._before_build_children(children)
        children = self._build_children(children)
        self._after_build_children(children)

        if self.is_built:
            self._children = children
            children = [self]
        return children

    def _build_children(self, children: list[BaseComponent]) -> list[BaseComponent]:
        lst: list[BaseComponent] = []
        for child in children:
            lst.extend(self._children_to_list(child.full_build(self.context)))
        return lst

    def _before_build(self) -> None:
        return None

    def _after_build(self, components: list[BaseComponent]) -> None:
        return None

    def _before_build_children(self, children: list[BaseComponent]) -> None:
        self.context.push_data(self._handle_provide(DataDict()))

    def _after_build_children(self, children: list[BaseComponent]) -> None:
        self.context.pop_frame()

    def _prepare_build(self, context: Context) -> None:
        self._build_data = ContextFrame(self)
        self._build_context = context

    def _finish_build(self) -> None:
        self._build_data = ContextFrame(self)
        self._build_context = None

    def _extract_attributes_from_kwargs(self, **kwargs: Any) -> None:
        for attr, value in kwargs.items():
            if attr in ALL_ATTRIBUTES:
                self._attributes.add(ALL_ATTRIBUTES[attr](value))


    def _handle_provide(self, data: DataDict) -> DataDict:
        BaseComponent.provide(self, data)
        return data

    def _handle_init_string(self, s: str) -> None:
        self._attributes.add(classes(s))

    def _unwrap_component_list(self, components: list[BaseComponent]) -> ComponentLike:
        match len(components):
            case 0:
                return None
            case 1:
                return components[0]
            case _:
                return components

    def _init_attributes(self, attr_like: Iterable[AttributeLike]) -> None:
        for attribute in attr_like:
            match attribute:
                case str():
                    self._handle_init_string(attribute)
                case Attribute():
                    self._attributes.add(attribute)
                case Attributes():
                    self._attributes.update(attribute)
                case Iterable():
                    self._init_attributes(attribute)
                case _:
                    raise ValueError(
                        f"Invalid attribute type: {type(attribute)} on {self.__class__.__name__}."
                    )

    def _verbose_string_parts(self) -> Iterable[str]:
        return (str(self.attributes),)

    def __str__(self) -> str:
        v_content = " | ".join(filter(bool, self._verbose_string_parts()))
        if v_content:
            return f"{self.__class__.__name__}({v_content})"
        else:
            return self.__class__.__name__

    def __getitem__(self, children: Children, **kwargs: Any) -> Self: 
        # Note: This method is overwritten in Component without super call
        copy = self.__class__(
            *self._attributes if not self._building else [],
            children=children,
            htpy_kwargs=self._htpy_kwargs,
            **self.props,
            **self.kwargs,
            **kwargs,
        )
        # break potential build recursion:
        copy._is_built = self._building
        return copy

    def __class_getitem__(cls, children: Children, **kwargs: Any) -> Self:
        return cls(children=children, **kwargs)

    def to_string(
        self,
        pretty: bool = False,
        verbose: bool = False,
        level: int = 0,
        tab_length: int = 4,
    ) -> str:
        pre_str = (" " * level * tab_length + ("- " if self._children else "")) * int(
            pretty
        )
        v_str = str(self) if verbose else self.__class__.__name__
        if pretty:
            child_str = "".join(
                "\n" + c.to_string(pretty, verbose, level + 1) for c in self._children
            )
        else:
            if self._children:
                child_str = f"[{', '.join(c.to_string(pretty, verbose, level + 1) for c in self._children)}]"
            else:
                child_str = ""
        return f"{pre_str}{v_str}{child_str}"

    def _children_to_list(self, children: Children) -> list[BaseComponent]:
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
                lst: list[BaseComponent] = []
                for child in children:
                    lst.extend(self._children_to_list(child))
                return lst
            case Callable():
                return [TemplateComponent(template_function=children)]
            case _:
                raise ValueError("Invalid child type: " + str(type(children)))


class Component(BaseComponent):
    def __init__(
        self,
        *modifiers: ModifierLike,
        component_theme: ComponentTheme | None = None,
        children: Children = None,
        htpy_kwargs: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            children=children,
            htpy_kwargs=htpy_kwargs,
            **kwargs,
        )
        self._component_theme = component_theme
        self._modifiers = Modifiers()
        self._init_modifiers(modifiers)

    @property
    def modifiers(self) -> Modifiers:
        if self.is_built:
            return self._modifiers
        return self._build_data.get(Modifiers) or Modifiers()

    @modifiers.setter
    def modifiers(self, value: Modifiers) -> None:
        if self.is_built:
            self._modifiers = value
        self._build_data[Modifiers] = value

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
    def provide(self, data: DataDict) -> None:
        if self._modifiers and not self.is_built:
            data[Modifiers] = self._modifiers

    @override
    def consume(self) -> None:
        super().consume()
        inherited_modifiers = self.context.get(Modifiers) or Modifiers()
        self.modifiers = inherited_modifiers | self._modifiers

    @override
    def _handle_provide(self, data: DataDict) -> DataDict:
        data = super()._handle_provide(data)
        self.__class__.provide(self, data)
        return data

    @override
    def _before_build(self) -> None:
        """Called before components are built and anything is inherited"""
        super()._before_build()
        for modifier in self.modifiers:
            modifier.apply_before_build(self.context, self)

    @override
    def _after_build(self, children: list[BaseComponent]) -> None:
        """Called after components are built and inheritance is handled."""
        super()._after_build(children)

        # or in future: context.get(Theme).get_component_theme(self)
        theme = self._component_theme
        for i, component in enumerate(children):
            if not isinstance(component, Component):
                continue
            if theme:
                component = theme.modify_build(self.context, component)
                component.attributes = theme.modify_attributes(component.attributes)
            for modifier in self.modifiers:
                component = modifier.apply_to_child(self.context, component)
            children[i] = component

    @override
    def _verbose_string_parts(self) -> Iterable[str]:
        return (
            str(self.attributes),
            str(self.modifiers),
        )

    @override
    def __getitem__(self, children: Children, **kwargs: Any) -> Self:
        copy = self.__class__(
            *self._attributes if not self._building else [],
            *self._modifiers if not self._building else [],
            children=children,
            component_theme=self._component_theme,
            htpy_kwargs=self._htpy_kwargs,
            **self.props,
            **self.kwargs,
            **kwargs,
        )
        copy._is_built = self._building
        return copy

    def _init_modifiers(self, mod_like: Iterable[ModifierLike]) -> None:
        for modifier in mod_like:
            match modifier:
                case str():
                    self._handle_init_string(modifier)
                case Attribute():
                    self._attributes.add(modifier)
                case Attributes():
                    self._attributes.update(modifier)
                case Modifier():
                    self._modifiers.add(modifier)
                case Modifiers():
                    self._modifiers.update(modifier)
                case Iterable():
                    self._init_modifiers(modifier)
                case _:
                    raise ValueError("Invalid modifier type.")


class VoidComponentMixin:
    # ignore return types, since mypy does not handle mro in mixins well

    def __getitem__(self, children: Children, **kwargs: Any) -> Self:
        if children:
            raise ValueError(f"{self.__class__.__name__} does not accept any children.")
        return super().__getitem__(children, **kwargs)

    def __class_getitem__(cls, children: Children, **kwargs: Any) -> Self:
        if children:
            raise ValueError(f"{cls.__name__} does not accept any children.")
        return super().__getitem__(children, **kwargs)


class SingleChildComponentMixin:
    def __getitem__(self, children: Children, **kwargs: Any) -> BaseComponent:
        if (
            isinstance(children, Sequence)
            and not isinstance(children, str)
            and len(children) != 1
        ):
            raise ValueError(
                f"{self.__class__.__name__} only accepts exactly one child."
            )
        return super().__getitem__(children, **kwargs)

    def __class_getitem__(cls, children: Children, **kwargs: Any) -> Self:
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


class TemplateComponent(Component):
    """Builds the given template_function during the render process."""

    def __init__(
        self,
        *modifiers: ModifierLike,
        template_function: TemplateFunctionType | None = None,
        component_theme: ComponentTheme | None = None,
        children: Children = None,
        htpy_kwargs: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            *modifiers,
            component_theme=component_theme,
            children=children,
            htpy_kwargs=htpy_kwargs,
            **kwargs,
        )
        self.template_function = template_function

    @override
    def full_build(self, context: Context) -> ComponentLike:
        """The component should return to its original state after building."""

        self._prepare_build(context)
        self.consume()
        self._before_build()
        return self

    @override
    def _handle_build(self) -> list[BaseComponent]:
        children = self._children
        if not self.is_built:
            self._building = True
            children = self._children_to_list(self.build(self.context, self._children))
            self._building = False

        self._before_build_children(children)
        children = self._build_children(children)
        self._after_build_children(children)

        if self.is_built:
            self._children = children
            children = [self]
        return children
    
    @override
    def _prepare_build(self, context: Context) -> None:
        self._build_data = ContextFrame(self)
        self._build_context = context.copy()

    @override
    def render(self) -> htpy.Node:
        children = self._handle_build()
        self._after_build(children)
        return [child.render() for child in children]

    @override
    def build(self, context: Context, children: Children) -> Children:
        if self.template_function is None:
            raise ValueError("TemplateComponent requires a template_function to build.")
        return self.template_function(context)
    
    @override
    def __getitem__(self, children: Children, **kwargs: Any) -> Self:
        return super().__getitem__(children, template_function=self.template_function, **kwargs)


@final
class Text(VoidComponentMixin, BuildsItselfMixin, Component):
    def __init__(self, *args: Any, text: str = "", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.text = text

    @override
    def render(self) -> str:
        return self.text

    @override
    def __getitem__(self, children: Children, **kwargs: Any) -> Self:
        return super().__getitem__(children, text=self.text, **kwargs)

    @override
    def _verbose_string_parts(self) -> Iterable[str]:
        return (f"text='{self.text}'", str(self.attributes), str(self.modifiers))
