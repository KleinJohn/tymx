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


from django_compose.base.helpers import BaseModel, class_or_instance_method

from attrs import field, evolve

if TYPE_CHECKING:
    import htpy


class ValidationError(Exception):
    pass


def wrap_components(components: Children) -> Component:
    """Wraps the given components in a Fragment for easier handling as a single component."""
    return Fragment(children=components)


def validate_is_built(components: Sequence[BaseComponent]) -> None:
    for component in components:
        if not component.is_built:
            raise ValidationError(f"{component.__class__.__name__} is not built!")
        validate_is_built(component.children)


def _convert_children_to_list(children: Children) -> list[BaseComponent]:
    def convert_children_recursive(
        children: Children, result: list[BaseComponent]
    ) -> None:
        match children:
            case None:
                return
            case type():
                result.append(children())
            case str():
                result.append(Text(text=children))
            case BaseComponent():
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

    result: list[BaseComponent] = []
    convert_children_recursive(children, result)
    return result


def _convert_children_to_tuple(
    children: Children,
) -> tuple[BaseComponent, ...]:
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


class BuildData(BaseModel):
    component: BaseComponent
    context: Context
    result: list[BaseComponent] = field(factory=list)
    data: DataDict = field(factory=DataDict)

    @classmethod
    def from_component(
        cls, component: BaseComponent, context: Context, data: DataDict | None = None
    ) -> Self:
        return cls(
            component=component,
            context=context,
            data=DataDict(data or {}),
        )

    @property
    def children(self) -> list[BaseComponent]:
        return self.result

    @property
    def attributes(self) -> Attributes:
        return self.data[Attributes]

    @attributes.setter
    def attributes(self, value: Attributes) -> None:
        self.data[Attributes] = value

    @property
    def modifiers(self) -> Modifiers:
        return self.data[Modifiers]

    @modifiers.setter
    def modifiers(self, value: Modifiers) -> None:
        self.data[Modifiers] = value


class Builder(BaseModel, frozen=True):
    data: BuildData = field(kw_only=False)

    @abstractmethod
    def build(self) -> list[BaseComponent]:
        """The result will be written into Builder.data.result and returned for convenience."""
        ...


class DefaultBuilder(Builder, frozen=True):
    """Handles building the component tree.
    The builder should be fully dependent on the supplied BuildData object.
    ### Build Process
    **Forward Pass**    (from root to leaves)
    1. Consume parent provided data into build data's attributes and modifiers
    2. Apply modifier.apply to the build data
    3. Push own provided data onto the context
    4. Call component's build method with unbuilt children
    5. Recursively build any components returned from build method
    6. Call build_self with the built results

    **Backward Pass**   (from leaves to root)
    1. Pop own provided data from the context
    2. Apply modifier.transform to the built result
    """

    data: BuildData

    @override
    def build(self) -> list[BaseComponent]:
        self._before_build()
        with self.data.context.frame(self.data.component):
            children = self._collect_children()
            self.data.result = self._handle_build(children)
        self._after_build()
        return self.data.result

    def _collect_children(self) -> list[BaseComponent]:
        """Collects unbuilt children to be passed to the build method."""
        return list(self.data.component.children)

    def _before_build(self) -> None:
        self.data.component.consume(self.data)
        for modifier in self.data.modifiers:
            modifier.apply(self.data)

    def _handle_build(self, children: list[BaseComponent]) -> list[BaseComponent]:
        built = _convert_children_to_list(
            self.data.component.build(self.data, children)
        )
        result: list[BaseComponent] = []
        for component in built:
            if component.is_built:
                result.append(component)
            else:
                result.extend(component.full_build(self.data.context))
        return _convert_children_to_list(
            self.data.component.build_self(self.data, result)
        )

    def _after_build(self) -> None:
        result = self.data.result
        for modifier in self.data.modifiers:
            result = modifier.transform(result)
        self.data.result = result


class BaseComponent(BaseModel, auto_frozen=True):
    builder: ClassVar[type[Builder]] = DefaultBuilder

    _items: ModifiersOrAttributes = field(
        alias="modifiers", repr=False, kw_only=False, default=None
    )
    modifiers: FrozenModifiers = field(init=False)
    attributes: FrozenAttributes = field(init=False)
    children: tuple[BaseComponent, ...] = field(
        default=None, converter=_convert_children_to_tuple
    )
    htpy_kwargs: dict[str, str] = field(factory=dict)
    is_built: bool = field(default=False)

    def __attrs_post_init__(self) -> None:
        attrs, mods = _split_attributes_and_modifiers(self._items)
        object.__setattr__(self, "modifiers", FrozenModifiers(mods))
        object.__setattr__(self, "attributes", FrozenAttributes(attrs))
        super().__attrs_post_init__()

    @abstractmethod
    def build(self, build: BuildData, children: Children) -> Children: ...

    @abstractmethod
    def render(self) -> htpy.Node: ...

    @class_or_instance_method
    def with_attributes(self_or_cls, **attributes: Any) -> Self:
        if isinstance(self_or_cls, type):
            cls = cast(type[Self], self_or_cls)
            return cls(_extract_additional_attributes(attributes))
        else:
            self = cast(Self, self_or_cls)
            new_attrs = self.attributes.merge(
                _extract_additional_attributes(attributes)
            )
            return evolve(self, modifiers=[new_attrs, self.modifiers])

    def provide(self, data: DataDict) -> None:
        if self.attributes:
            data[Attributes] = self.attributes
        if self.modifiers:
            data[Modifiers] = self.modifiers

    def consume(self, build: BuildData) -> None:
        inherited_attributes = build.context.get(Attributes) or Attributes()
        build.attributes = inherited_attributes | self.attributes
        inherited_modifiers = build.context.get(Modifiers) or Modifiers()
        build.modifiers = inherited_modifiers | self.modifiers

    def full_build(self, context: Context) -> list[BaseComponent]:
        """The component should return to its original state after building."""
        build_data = BuildData.from_component(self, context)
        return self.builder(data=build_data).build()

    def copy_with_children(self, children: Children, **update_kwargs: Any) -> Self:
        return evolve(
            self, children=_convert_children_to_tuple(children), **update_kwargs
        )

    def build_self(self, build: BuildData, children: Children) -> Children:
        """Returns a copy of this component with given children and is_built=True flag."""
        return children

    def to_string(
        self,
        pretty: bool = False,
        verbose: bool = False,
        level: int = 0,
        tab_length: int = 4,
    ) -> str:
        pre_str = (" " * level * tab_length + ("- " if self.children else "")) * int(
            pretty
        )
        v_str = str(self) if verbose else self.__class__.__name__
        if pretty:
            child_str = "".join(
                "\n" + c.to_string(pretty, verbose, level + 1) for c in self.children
            )
        else:
            if self.children:
                child_str = f"[{', '.join(c.to_string(pretty, verbose, level + 1) for c in self.children)}]"
            else:
                child_str = ""
        return f"{pre_str}{v_str}{child_str}"

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


class Component(BaseComponent):
    """Extends BaseComponent with support for themes."""

    theme: Optional[Theme] = None

    @abstractmethod
    def build(self, build: BuildData, children: Children) -> Children: ...

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
        super().provide(data)
        if self.theme:
            data[Theme] = self.theme

    @override
    def consume(self, build: BuildData) -> None:
        super().consume(build)
        build.data[Theme] = self.theme or build.context.get(Theme)


class NoChildren:
    def __attrs_post_init__(self) -> None:
        component = cast(Component, self)
        if component.children:
            raise ValueError(
                f"Component '{component.__class__.__name__}' cannot have children."
            )
        super().__attrs_post_init__()  # type: ignore


class Renderable(ABC):
    @abstractmethod
    def render(self) -> htpy.Renderable: ...

    def build(self, build: BuildData, children: Children) -> Children:
        return children

    def build_self(self, build: BuildData, children: Children) -> Children:
        component = cast(BaseComponent, self)
        return component.copy_with_children(
            children, modifiers=[build.attributes, build.modifiers], is_built=True
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
class Text(NoChildren, Renderable, Component):
    text: str = ""

    @override
    def render(self) -> htpy.Renderable:
        return htpy.fragment[self.text]

    @override
    def _verbose_string_parts(self) -> Iterable[str]:
        return (f"text='{self.text}'", str(self.attributes), str(self.modifiers))


class Fragment(Component):

    @override
    def build(self, build: BuildData, children: Children) -> Children:
        return children

    @override
    def to_string(
        self,
        pretty: bool = False,
        verbose: bool = False,
        level: int = 0,
        tab_length: int = 4,
    ) -> str:
        return "\n".join(
            child.to_string(pretty, verbose, level, tab_length)
            for child in self.children
        )
