from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Sequence
from typing import TYPE_CHECKING, ClassVar, cast

from typing_extensions import (
    Any,
    Self,
    Optional,
    final,
    override,
)

from django_compose.base.context import Context, DataDict
from django_compose.base.attributes import (
    Attribute,
    Attributes,
    FrozenAttributes,
    ALL_ATTRIBUTES,
)
from django_compose.base.modifiers.base_modifiers import (
    FrozenModifiers,
    Modifier,
    Modifiers,
)
from django_compose.base.theme import Theme
from django_compose.base.types import (
    Children,
    ModifiersOrAttributes,
)
from django_compose.base.config import attribute_string_handler


from django_compose.base.helpers import BaseModel, classinstancemethod

from attrs import field, evolve

if TYPE_CHECKING:
    import htpy


def wrap_components(components: Children) -> Component:
    """Wraps the given components in a Fragment for easier handling as a single component."""
    return Fragment(children=components)


def _convert_children_to_list(children: Children) -> list[Component]:
    def convert_children_recursive(children: Children, result: list[Component]) -> None:
        match children:
            case None:
                return
            case type():
                result.append(children())
            case str():
                result.append(Text(text=children))
            case Component():
                result.append(children)
            case Sequence():
                for child in children:
                    convert_children_recursive(child, result)
            case Callable():
                # TODO
                # return [TemplateComponent(template_function=children)]
                result.append(Text(text="UNDEFINED"))
            case _:
                raise ValueError("Invalid child type: " + str(type(children)))

    result: list[Component] = []
    convert_children_recursive(children, result)
    return result


def _convert_children_to_tuple(
    children: Children,
) -> tuple[Component, ...]:
    return tuple(_convert_children_to_list(children))


def _extract_additional_attributes(extra_dict: dict[str, Any]) -> list[Attribute]:
    attrs: list[Attribute] = []
    for attr, value in extra_dict.items():
        if attr in ALL_ATTRIBUTES:
            attrs.append(ALL_ATTRIBUTES[attr](value))
    return attrs


def _split_attributes_and_modifiers(
    items: ModifiersOrAttributes,
) -> tuple[list[Attribute], list[Modifier]]:
    def split_recursive(
        item: ModifiersOrAttributes,
        attrs: list[Attribute],
        mods: list[Modifier],
    ) -> None:
        match item:
            case None:
                return
            case str():
                attrs.append(attribute_string_handler(item))
            case Attribute():
                attrs.append(item)
            case Modifier():
                mods.append(item)
            case Attributes():
                attrs.extend(item)
            case Modifiers():
                mods.extend(item)
            case Sequence():
                for i in item:
                    split_recursive(i, attrs, mods)
            case _:
                raise ValueError(f"Invalid attribute/modifier: {item}")

    attrs: list[Attribute] = []
    mods: list[Modifier] = []
    split_recursive(items, attrs, mods)
    return attrs, mods


def _convert_inputs_to_modifiers(items: ModifiersOrAttributes) -> FrozenModifiers:
    match items:
        case None | Modifier() | Modifiers():
            return FrozenModifiers(items)
        case Sequence():
            mods: list[Modifier] = []
            for m in items:
                mods.extend(_convert_inputs_to_modifiers(m))
            return FrozenModifiers(mods)
        case _:
            return FrozenModifiers()


def _convert_inputs_to_attributes(items: ModifiersOrAttributes) -> FrozenAttributes:
    match items:
        case None | Attribute() | Attributes() | str():
            return FrozenAttributes(items)
        case Sequence():
            attrs: list[Attribute] = []
            for a in items:
                attrs.extend(_convert_inputs_to_attributes(a))
            return FrozenAttributes(attrs)
        case _:
            return FrozenAttributes()


class Builder(BaseModel, frozen=True):
    context: Context = field(kw_only=False)

    @abstractmethod
    def build(self, component: Component) -> list[Component]:
        """Builds the given component and returns a list of built components to
        replace it in the tree."""
        ...


class DefaultBuilder(Builder, frozen=True):
    """Handles building the component tree.
    The builder should be fully dependent on the supplied BuildData object.
    ### Build Process
    **Forward Pass**    (from root to leaves)
    1. Consume parent's provided data
    2. Apply modifier.apply to the build data
    3. Push own provided data onto the context
    4. Call component's build method with unbuilt children
    5. Recursively build any components returned from build method

    **Backward Pass**   (from leaves to root)
    1. Pop own provided data from the context
    2. Call build_self with the built results
    3. Apply modifier.transform to the built result
    """

    context: Context = field(kw_only=False)

    @override
    def build(self, component: Component) -> list[Component]:
        self._before_build(component)
        returned = self._call_build()
        built = self._build_returned(returned)
        return self._after_build(built)

    def _before_build(self, component: Component) -> None:
        self.context.create_data(component)
        component.consume(self.context)
        for modifier in self.context.data.modifiers:
            modifier.apply(self.context)

    def _call_build(self) -> list[Component]:
        component = self.context.data.component
        return _convert_children_to_list(component.build(self.context))

    def _build_returned(self, returned: list[Component]) -> list[Component]:
        result: list[Component] = []
        provide_data = DataDict()
        self.context.data.component.provide(provide_data)
        with self.context.frame(provide_data):
            for child in returned:
                if child.is_built:
                    result.append(child)
                else:
                    result.extend(child.full_build(self.context))
        return _convert_children_to_list(self.context.data.component.compose(self.context, result))

    def _after_build(self, result: list[Component]) -> list[Component]:
        for modifier in self.context.data.modifiers:
            result = modifier.transform(result)
        return result


class Component(BaseModel, auto_frozen=True):
    builder: ClassVar[type[Builder]] = DefaultBuilder
    builds_itself: ClassVar[bool] = False

    _items: ModifiersOrAttributes = field(
        alias="modifiers", repr=False, kw_only=False, default=None
    )
    modifiers: FrozenModifiers = field(init=False)
    attributes: FrozenAttributes = field(init=False)
    children: tuple[Component, ...] = field(default=None, converter=_convert_children_to_tuple)
    theme: Optional[Theme] = None
    htpy_kwargs: dict[str, str] = field(factory=dict)
    is_built: bool = field(default=False)

    def __attrs_post_init__(self) -> None:
        attrs, mods = _split_attributes_and_modifiers(self._items)
        object.__setattr__(self, "modifiers", FrozenModifiers(mods))
        object.__setattr__(self, "attributes", FrozenAttributes(attrs))
        super().__attrs_post_init__()

    @classinstancemethod
    def with_attributes(self_or_cls, **attributes: Any) -> Self:
        if isinstance(self_or_cls, type):
            cls = cast(type[Self], self_or_cls)
            return cls(_extract_additional_attributes(attributes))
        else:
            self = cast(Self, self_or_cls)
            new_attrs = self.attributes.merge(_extract_additional_attributes(attributes))
            return evolve(self, modifiers=[new_attrs, self.modifiers])

    @abstractmethod
    def build(self, context: Context) -> Children:
        """Defines the strategy for replacing this component in the forward pass."""
        ...

    def render(self) -> htpy.Node:
        # Can omit render method if build method returns other components.
        raise NotImplementedError(
            "Render method not implemented. "
            "- Most likely called render on an unbuilt component. "
            "Make sure your components build down to html."
        )

    def compose(self, context: Context, children: Children) -> Children:
        """Defines the strategy for replacing this component in the backward pass.

        The given children are at this point already built.
        By default, the component is replaced with its children. Renderable components
        instead return themselves with the built children replacing the unbuilt ones
        and the is_built flag set to True.
        """
        return children

    def full_build(self, context: Context) -> list[Component]:
        """The component should return to its original state after building."""
        return self.builder(context).build(self)

    def provide(self, data: DataDict) -> None:
        if self.attributes:
            data[Attributes] = self.attributes
        if self.modifiers:
            data[Modifiers] = self.modifiers
        if self.theme:
            data[Theme] = self.theme

    def consume(self, context: Context) -> None:
        inherited_attributes = context.get(Attributes) or Attributes()
        context.data.attributes = inherited_attributes | self.attributes
        inherited_modifiers = context.get(Modifiers) or Modifiers()
        context.data.modifiers = inherited_modifiers | self.modifiers

        inherited_theme = self.theme or context.get(Theme)
        if inherited_theme:
            context.data[Theme] = inherited_theme

    def copy_with_children(self, children: Children, **update_kwargs: Any) -> Self:
        return evolve(self, children=_convert_children_to_tuple(children), **update_kwargs)

    def to_string(
        self,
        pretty: bool = False,
        verbose: bool = False,
        level: int = 0,
        _last: bool = True,
        _prefix: str = "",
    ) -> str:
        v_str = str(self) if verbose else self.__class__.__name__

        if not pretty:
            if self.children:
                child_str = f"[{', '.join(c.to_string(False, verbose) for c in self.children)}]"
            else:
                child_str = ""
            return f"{v_str}{child_str}"

        connector = "└── " if _last else "├── "
        line = (_prefix + connector + v_str) if level > 0 else v_str

        if not self.children:
            return line

        child_prefix = _prefix + ("    " if _last else "│   ")
        child_lines = [
            c.to_string(
                True, verbose, level + 1, _last=(i == len(self.children) - 1), _prefix=child_prefix
            )
            for i, c in enumerate(self.children)
        ]
        return line + "\n" + "\n".join(child_lines)

    def _verbose_string_parts(self) -> Iterable[str]:
        return (
            str(self.attributes),
            str(self.modifiers),
        )

    def __str__(self) -> str:
        v_content = " | ".join(filter(bool, self._verbose_string_parts()))
        if v_content:
            return f"{self.__class__.__name__}({v_content})"
        else:
            return self.__class__.__name__

    def __getitem__(self, *children: Children) -> Self:
        return self.copy_with_children(children)

    def __class_getitem__(cls: type[Self], *children: Children) -> Self:
        return cls(children=_convert_children_to_tuple(children))

    def __bool__(self) -> bool:
        return True


class NoChildren(Component):

    @override
    def __attrs_post_init__(self) -> None:
        if self.children:
            raise ValueError(f"Component '{self.__class__.__name__}' cannot have children.")
        super().__attrs_post_init__()  # type: ignore


class NoInheritance(Component):

    @override
    def consume(self, context: Context) -> None:
        # Do not consume any attributes, modifiers, or theme etc.
        pass

    @override
    def provide(self, data: DataDict) -> None:
        # Do not provide any attributes, modifiers, or theme etc.
        pass


class RenderableComponent(Component, ABC):
    """Mixin on Component for components that build and render themselves."""

    builds_itself = True

    @abstractmethod
    def render(self) -> htpy.Renderable: ...

    @override
    def build(self, context: Context) -> Children:
        return self.children

    @override
    def compose(self, context: Context, children: Children) -> Children:
        """Renderable components return themselves with the is_built flag set to True."""
        return self.copy_with_children(
            children, modifiers=[context.data.attributes, context.data.modifiers], is_built=True
        )


class TemplateComponent(Component):
    """Builds the given template_function during the render process."""

    pass


#     def __init__(
#         self,
#         *modifiers: ModifiersOrAttributes,
#         template_function: TemplateFunctionType | None = None,
#         children: Children = None,
#         theme: Theme | None = None,
#         htpy_kwargs: dict[str, str] | None = None,
#         **kwargs: Any,
#     ) -> None:
#         super().__init__(
#             *modifiers,
#             children=children,
#             theme=theme,
#             htpy_kwargs=htpy_kwargs,
#             **kwargs,
#         )
#         self.template_function = template_function

#     @override
#     def full_build(self, context: Context) -> ComponentLike:
#         """The component should return to its original state after building."""

#         self._prepare_build(context)
#         self.consume()
#         self._before_build()
#         return self

#     @override
#     def _handle_build(self) -> list[BaseComponent]:
#         children = self._children
#         if not self.is_built:
#             self._building = True
#             children = self._children_to_list(self.build(self.context, self._children))
#             self._building = False

#         self._before_build_children(children)
#         children = self._build_children(children)
#         self._after_build_children(children)

#         if self.is_built:
#             self._children = children
#             children = [self]
#         return children

#     @override
#     def _prepare_build(self, context: Context) -> None:
#         self._build_data = ContextFrame(self)
#         self._build_context = context.copy()

#     @override
#     def render(self) -> htpy.Node:
#         children = self._handle_build()
#         self._after_build(children)
#         return [child.render() for child in children]

#     @override
#     def build(self, context: Context, children: Children) -> Children:
#         if self.template_function is None:
#             raise ValueError("TemplateComponent requires a template_function to build.")
#         return self.template_function(context)

#     @override
#     def __getitem__(self, children: Children, **kwargs: Any) -> Self:
#         return super().__getitem__(
#             children, template_function=self.template_function, **kwargs
#         )


class ThemedComponent(Component):
    """A component that maps its children through a function during the build process."""

    pass


#     def __init__(self, *modifiers: ModifiersOrAttributes, **kwargs: Any) -> None:
#         super().__init__(*modifiers, **kwargs)
#         self._smods = modifiers  # stored args for from_theme
#         self._skwargs = kwargs  # stored kwargs for from_theme

#     @abstractmethod
#     def from_theme(
#         self, theme: Theme, *smods: ModifiersOrAttributes, **skwargs: Any
#     ) -> Component: ...

#     @override
#     def full_build(self, context: Context) -> ComponentLike:
#         theme = self._theme or Theme.of(context)
#         if theme is None:
#             raise ValueError("Theme is required to build ThemedComponent.")
#         component = self.from_theme(theme, *self._smods, **self._skwargs)
#         return component.full_build(context)

#     @override
#     def build(self, context: Context, children: Children) -> Children:
#         raise NotImplementedError(
#             "MappedComponent should not implement build, full_build is overridden."
#         )


@final
class Text(NoInheritance, NoChildren, RenderableComponent, Component):
    text: str = ""

    @override
    def render(self) -> htpy.Renderable:
        return htpy.fragment[self.text]

    @override
    def _verbose_string_parts(self) -> Iterable[str]:
        return (f"text='{self.text}'", str(self.attributes), str(self.modifiers))


@final
class Fragment(NoInheritance, Component):

    @override
    def build(self, context: Context) -> Children:
        return self.children

    @override
    def to_string(
        self,
        pretty: bool = False,
        verbose: bool = False,
        level: int = 0,
        _last: bool = True,
        _prefix: str = "",
    ) -> str:
        return "\n".join(
            c.to_string(
                pretty, verbose, level, _last=(i == len(self.children) - 1), _prefix=_prefix
            )
            for i, c in enumerate(self.children)
        )
