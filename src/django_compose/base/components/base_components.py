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


from pydantic import BaseModel, ConfigDict, Field, model_validator

if TYPE_CHECKING:
    import htpy


def _convert_children_to_list(children: Children) -> list[BaseComponent]:
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
                lst.extend(_convert_children_to_list(child))
            return lst
        case Callable():
            # TODO
            # return [TemplateComponent(template_function=children)]
            return [Text(text="UNDEFINED")]
        case _:
            raise ValueError("Invalid child type: " + str(type(children)))


def _extract_additional_attributes(extra_dict: dict[str, Any]) -> Attributes:
    attrs = Attributes()
    for attr, value in extra_dict.items():
        if attr in ALL_ATTRIBUTES:
            attrs.add(ALL_ATTRIBUTES[attr](value))
    return attrs


def _split_attributes_and_modifiers(
    items: Sequence[ModifiersOrAttributes],
) -> tuple[Attributes, Modifiers]:
    attrs = Attributes()
    mods = Modifiers()
    for item in items:
        if item is None:
            continue
        elif isinstance(item, Attribute):
            attrs.add(item)
        elif isinstance(item, Modifier):
            mods.add(item)
        elif isinstance(item, Attributes):
            attrs.update(item)
        elif isinstance(item, Modifiers):
            mods.update(item)
        elif isinstance(item, Sequence) and not isinstance(item, str):
            sub_attrs, sub_mods = _split_attributes_and_modifiers(item)
            attrs.update(sub_attrs)
            mods.update(sub_mods)
        else:
            raise ValueError(f"Invalid attribute/modifier: {item}")
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
    result: list[BaseComponent] = Field(default_factory=list)
    data: DataDict = Field(default_factory=DataDict)

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


class Builder(BaseModel, ABC):
    model_config = ConfigDict(frozen=True)

    data: BuildData = Field(kw_only=False)

    @abstractmethod
    def build(self) -> None: ...


class DefaultBuilder(Builder):
    """Handles building the component tree.

    The builder should be fully dependent on the supplied BuildData object.
    # Build Process

    **Forward Pass**
        1. Push data to be provided onto the context
        2. Fully build children

    **Backward Pass**
        3. Remove own provided data from the context
        4. Consume data provided by parents into data's DataDict
        5. Build the component by supplying the built children and write result to data.result
    """

    data: BuildData

    @override
    def build(self) -> None:
        """The result will be written into Builder.data.result"""
        self._before_build_children()
        children = self._build_children()
        self._after_build_children()
        self._before_build()
        self._handle_build(children)
        self._after_build()

    def _before_build_children(self) -> None:
        data: DataDict = DataDict()
        self.data.component.provide(data)
        self.data.context.push_data(data)

    def _build_children(self) -> list[BaseComponent]:
        """Builds component's children entirely based on the previously prepared context."""
        lst: list[BaseComponent] = []
        for child in self.data.component.children:
            lst.extend(child.full_build(self.data.context))
        return lst

    def _after_build_children(self) -> None:
        self.data.context.pop_frame()

    def _before_build(self) -> None:
        self.data.component.consume(self.data)
        for modifier in self.data.modifiers:
            modifier.apply(self.data)

    def _handle_build(self, children: list[BaseComponent]) -> None:
        # first, build children entirely based on context
        self.data.result = _convert_children_to_list(
            self.data.component.build(self.data, children)
        )

    def _after_build(self) -> None:
        for modifier in self.data.modifiers:
            modifier.transform(self.data.result)


class BaseComponent(BaseModel, ABC):
    model_config = ConfigDict(extra="allow", frozen=True)
    builder: ClassVar[type[Builder]] = DefaultBuilder

    items: ModifiersOrAttributes = Field(
        default=None, kw_only=False, exclude=True, init_var=True
    )
    modifiers: FrozenModifiers = Field(init=False)
    attributes: FrozenAttributes = Field(init=False)
    _children: Children = Field(alias="children", default=None)
    htpy_kwargs: dict[str, str] = Field(default_factory=dict)
    is_built: bool = Field(default=False)

    def __init__(
        self,
        *items: ModifiersOrAttributes,
        children: Children = None,
        htpy_kwargs: dict[str, str] | None = None,
        is_built: bool = False,
        **kwargs: Any,
    ) -> None:
        init_attributes, init_modifiers = _split_attributes_and_modifiers(items)
        init_attributes.update(_extract_additional_attributes(kwargs))

        super().__init__(
            children=_convert_children_to_list(children),
            htpy_kwargs=htpy_kwargs or {},
            is_built=is_built,
            **kwargs,
        )
        # set frozen attributes (init=False):
        object.__setattr__(self, "attributes", FrozenAttributes(init_attributes))
        object.__setattr__(self, "modifiers", FrozenModifiers(init_modifiers))

    @property
    def children(self) -> list[BaseComponent]:
        return cast(list[BaseComponent], self._children)

    @abstractmethod
    def build(self, build: BuildData, children: Children) -> Children: ...

    @abstractmethod
    def render(self) -> htpy.Node: ...

    def provide(self, data: DataDict) -> None:
        if self.attributes:  # and not built
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
        if self.is_built:
            return [self]
        build_data = BuildData.from_component(self, context)
        self.builder(build_data).build()
        return build_data.result

    def copy_with_children(self, children: Children, **update_kwargs: Any) -> Self:
        return self.model_copy(update={"children": children, **update_kwargs})

    def build_self(self, children: Children) -> BaseComponent:
        """Returns a copy of this component with given children and is_built=True flag."""
        return self.copy_with_children(children, is_built=True)

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

    def __getitem__(self, children: Children) -> Self:
        return self.copy_with_children(children)

    def __class_getitem__(cls, children: Children) -> Self:
        return cls(children=children)

    def __bool__(self) -> bool:
        return True


class Component(BaseComponent):
    """Extends BaseComponent with support for themes."""

    theme: Optional[Theme] = None

    @abstractmethod
    def build(self, build: BuildData) -> Children: ...

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


class VoidComponentMixin:
    @model_validator(mode="after")
    def _validate_void_children(self) -> Self:
        component = cast(BaseComponent, self)
        if component.children:
            raise ValueError(f"{self.__class__.__name__} cannot have children.")
        return self


class SingleChildComponentMixin:
    @model_validator(mode="after")
    def _validate_single_child(self) -> Self:
        component = cast(BaseComponent, self)
        if len(component.children) != 1:
            raise ValueError(
                f"{self.__class__.__name__} only accepts exactly one child."
            )
        return self


class Renderable(ABC):
    @abstractmethod
    def render(self) -> htpy.Renderable: ...

    def build(self, build: BuildData, children: Children) -> BaseComponent:
        self = cast(BaseComponent, self)
        return self.build_self(children)


# class TemplateComponent(Component):
#     """Builds the given template_function during the render process."""

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


# class ThemedComponent(Component):
#     """A component that maps its children through a function during the build process."""

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
class Text(VoidComponentMixin, Renderable, Component):
    text: str = ""

    @override
    def render(self) -> str:
        return self.text

    @override
    def _verbose_string_parts(self) -> Iterable[str]:
        return (f"text='{self.text}'", str(self.attributes), str(self.modifiers))
