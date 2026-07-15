from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Sequence
from typing import (
    Any,
    ClassVar,
    Self,
    TypeVar,
    final,
    override,
)

import htpy
from attrs import evolve, field

from tymx.base.attributes import (
    ALL_ATTRIBUTES,
    Attribute,
    Attributes,
    FrozenAttributes,
)
from tymx.base.config import attribute_string_handler
from tymx.base.consumable import Consumable
from tymx.base.context import Context, DataDict
from tymx.base.helpers import BaseModel, classinstancemethod
from tymx.base.modifiers.base_modifiers import (
    FrozenModifiers,
    Modifier,
    Modifiers,
)
from tymx.base.theme import Theme
from tymx.base.types import (
    BuildFunctionType,
    Children,
    ModifiersOrAttributes,
)

T_Component = TypeVar("T_Component", bound="Component")


class ValidationError(Exception):
    pass


def wrap_components(components: Children) -> Component:
    """Wraps the given components in a Fragment for easier handling as a single component."""
    return Fragment(children=components, is_built=True)


def children_to_list(children: Children) -> list[Component]:
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
                result.append(TemplateComponent(template_function=children))
            case _:
                raise ValueError("Invalid child type: " + str(type(children)))

    result: list[Component] = []
    convert_children_recursive(children, result)
    return result


def children_to_tuple(
    children: Children,
) -> tuple[Component, ...]:
    return tuple(children_to_list(children))


def _extract_additional_attributes(extra_dict: dict[str, Any]) -> list[Attribute]:
    attrs: list[Attribute[Any]] = []
    for attr, value in extra_dict.items():
        if attr in ALL_ATTRIBUTES:
            attrs.append(ALL_ATTRIBUTES[attr](value))
    return attrs


def _split_attributes_and_modifiers(
    items: ModifiersOrAttributes,
) -> tuple[list[Attribute[Any]], list[Modifier]]:
    def split_recursive(
        item: ModifiersOrAttributes,
        attrs: list[Attribute[Any]],
        mods: list[Modifier],
    ) -> None:
        match item:
            case None:
                return
            case str():
                if item:
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

    attrs: list[Attribute[Any]] = []
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
            attrs: list[Attribute[Any]] = []
            for a in items:
                attrs.extend(_convert_inputs_to_attributes(a))
            return FrozenAttributes(attrs)
        case _:
            return FrozenAttributes()


def children_field(**kwargs) -> Any:
    return field(converter=children_to_tuple, **kwargs)


class Builder(BaseModel):
    context: Context = field(kw_only=False)

    @abstractmethod
    def build(self, component: Component) -> list[Component]:
        """Builds the given component and returns a list of built components to
        replace it in the tree."""
        ...


class ComponentBuilder(Builder):
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

    @override
    def build(self, component: Component) -> list[Component]:
        self._before_build(component)
        returned = self._call_build()
        built = self._build_returned(returned)
        composed = self._compose_built(built)
        return self._after_build(composed)

    def _before_build(self, component: Component) -> None:
        self.context.create_data(component)
        component.consume(self.context)
        modifiers = self.context.data.modifiers
        if modifiers is not None:
            modifiers.apply(self.context)

    def _call_build(self) -> list[Component]:
        component = self.context.data.component
        return children_to_list(component.build(self.context))

    def _build_returned(self, returned: list[Component]) -> list[Component]:
        result: list[Component] = []
        self.context.data.component.provide(self.context)
        with self.context.frame():
            for child in returned:
                if child.is_built:
                    result.append(child)
                else:
                    result.extend(child.full_build(self.context))
        return result

    def _compose_built(self, built: list[Component]) -> list[Component]:
        return children_to_list(
            self.context.data.component.compose(self.context, built)
        )

    def _after_build(self, result: list[Component]) -> list[Component]:
        modifiers = self.context.data.modifiers
        if modifiers is not None:
            result = modifiers.transform(result)
        return result


class Component(BaseModel, auto_frozen=True):
    __validate__: bool = field(init=False, default=True, repr=False)

    builder: ClassVar[type[Builder]] = ComponentBuilder
    builds_itself: ClassVar[bool] = False

    _items: ModifiersOrAttributes = field(
        alias="modifiers", repr=False, kw_only=False, default=None
    )
    modifiers: FrozenModifiers = field(init=False)
    attributes: FrozenAttributes = field(init=False)
    children: tuple[Component, ...] = field(converter=children_to_tuple, default=None)
    is_built: bool = field(default=False)

    @override
    def __attrs_post_init__(self) -> None:
        attrs, mods = _split_attributes_and_modifiers(self._items)
        object.__setattr__(self, "modifiers", FrozenModifiers(mods))
        object.__setattr__(self, "attributes", FrozenAttributes(attrs))
        super().__attrs_post_init__()
        self.modifiers.post_init(self)
        if self.__validate__:
            self._validate()

    @classinstancemethod
    def with_attributes(
        self: type[T_Component] | T_Component, **attributes: Any
    ) -> T_Component:
        if isinstance(self, type):
            return self(_extract_additional_attributes(attributes))
        else:
            new_attrs = self.attributes.merge(
                _extract_additional_attributes(attributes)
            )
            return evolve(self, modifiers=[new_attrs, self.modifiers])

    @abstractmethod
    def build(self, context: Context) -> Children:
        """Defines the strategy for replacing this component in the forward pass."""
        ...

    def render(self) -> htpy.Node:
        # Can omit render method if build method returns other components.
        raise NotImplementedError(
            f"Render method not implemented in {self.__class__.__name__}. "
            "- Most likely called render on an unbuilt component. "
            "Make sure your components build down to html."
        )

    def compose(self, context: Context, children: Children) -> Children:
        """Defines the strategy for replacing this component in the backward pass.

        The given children are at this point already built.
        By default, the component is replaced with its children. Renderable components
        instead return a copy of themselves with the built children replacing the
        unbuilt ones and the is_built flag set to True.
        """
        return children

    def full_build(self, context: Context) -> list[Component]:
        """The component should return to its original state after building."""
        return self.builder(context).build(self)

    def provide(self, context: Context) -> None:
        """Prepares context.data._inherited_data for children to consume."""
        if self.attributes:
            context.provide(self.attributes.copy_non_frozen())
        if self.modifiers:
            context.provide(self.modifiers.copy_non_frozen())

    def consume(self, context: Context) -> None:
        """Prepares context.data._component_data for this component to use."""
        context.consume(Attributes, default=Attributes(), merge=self.attributes)
        context.consume(Modifiers, default=Modifiers(), merge=self.modifiers)
        context.consume(Theme)

    def copy(self, **changes: Any) -> Self:
        """Copy with null. children=null will nullify children!"""
        return evolve(self, **changes)

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
                child_str = (
                    f"[{', '.join(c.to_string(False, verbose) for c in self.children)}]"
                )
            else:
                child_str = ""
            return f"{v_str}{child_str}"

        connector = "└── " if _last else "├── "
        line = (_prefix + connector + v_str) if level > 0 else v_str

        if not self.children:
            return line

        child_prefix = _prefix + ("    " if _last else "│   ") if level > 0 else _prefix
        child_lines = [
            c.to_string(
                True,
                verbose,
                level + 1,
                _last=(i == len(self.children) - 1),
                _prefix=child_prefix,
            )
            for i, c in enumerate(self.children)
        ]
        return line + "\n" + "\n".join(child_lines)

    def _verbose_string_parts(self) -> Iterable[str]:
        return (
            str(self.attributes),
            str(self.modifiers),
        )

    def _validate(self) -> None:
        pass

    def __getitem__(self, *children: Children) -> Self:
        return self.copy(children=children)

    def __class_getitem__(cls: type[Self], *children: Children) -> Self:
        return cls(children=children_to_tuple(children))

    def __call__(
        self,
        modifiers: ModifiersOrAttributes = None,
        *,
        children: Children = None,
        is_built: bool = False,
        **changes: Any,
    ) -> Self:
        """Copy without null. children=None will not change children."""
        all_changes = {
            **changes,
            "modifiers": modifiers,
            "children": children,
            "is_built": is_built,
        }
        all_changes = {k: v for k, v in all_changes.items() if v is not None}
        return self.copy(**all_changes)

    def __matmul__(self, other: ModifiersOrAttributes) -> Self:
        return self.copy(modifiers=[self.attributes, self.modifiers, other])

    def __rmatmul__(self, other: ModifiersOrAttributes) -> Self:
        return self.copy(modifiers=[other, self.attributes, self.modifiers])

    def __str__(self) -> str:
        v_content = " | ".join(filter(bool, self._verbose_string_parts()))
        if v_content:
            return f"{self.__class__.__name__}({v_content})"
        else:
            return self.__class__.__name__

    def __bool__(self) -> bool:
        return True

    def __mul__(self, other: int) -> list[Self]:
        if not isinstance(other, int):
            raise TypeError("Can only multiply Component by an integer.")
        return [self.copy() for _ in range(other)]

    def __rmul__(self, other: int) -> list[Self]:
        return self.__mul__(other)


class NoChildren(Component):
    @override
    def _validate(self) -> None:
        super()._validate()
        if self.children:
            raise ValidationError(
                f"Component '{self.__class__.__name__}' cannot have children."
            )


class NoInheritance(Component):

    @property
    def target(self) -> ModifiersOrAttributes:
        """Used to give the attributes/modifiers to another component instead of inheriting them to children."""
        return [self.attributes, self.modifiers]

    @final
    @override
    def consume(self, context: Context) -> None:
        # Do not consume any attributes, modifiers, or theme etc.
        pass

    @final
    @override
    def provide(self, context: Context) -> None:
        # Do not provide any attributes, modifiers, or theme etc.
        pass


class RenderableComponent(Component, ABC):
    """Mixin on Component for components that build and render themselves."""

    builds_itself = True

    @abstractmethod
    def render(self) -> htpy.Node: ...

    @override
    def build(self, context: Context) -> Children:
        return self.children

    @override
    def compose(self, context: Context, children: Children) -> Children:
        """Renderable components return themselves with the is_built flag set to True."""
        return self.copy(
            children=children,
            modifiers=[context.data.attributes, context.data.modifiers],
            is_built=True,
        )


@final
class Text(NoInheritance, NoChildren, RenderableComponent, Component):
    text: str = ""

    @override
    def render(self) -> htpy.Node:
        return self.text

    @override
    def _verbose_string_parts(self) -> Iterable[str]:
        return (f"text='{self.text}'", str(self.attributes), str(self.modifiers))


@final
class Fragment(NoInheritance, RenderableComponent, Component):
    @override
    def build(self, context: Context) -> Children:
        return self.children

    @override
    def render(self) -> htpy.Renderable:
        return htpy.fragment[(child.render() for child in self.children)]

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
                pretty,
                verbose,
                level,
                _last=(i == len(self.children) - 1),
                _prefix=_prefix,
            )
            for i, c in enumerate(self.children)
        )


class TemplateBuilder(ComponentBuilder):
    """Builder for TemplateComponent that calls template_function instead of build (if possible)."""

    @override
    def _call_build(self) -> list[Component]:
        component = self.context.data.component
        if (
            isinstance(component, TemplateComponent)
            and component.template_function is not None
        ):
            return children_to_list(component.template_function(self.context))
        return children_to_list(component.build(self.context))


class TemplateComponent(RenderableComponent, Component):
    """Delays the execution of `Component.build` to render time."""

    builder: ClassVar[type[Builder]] = TemplateBuilder
    builds_itself: ClassVar[bool] = False

    template_function: BuildFunctionType | None = None
    stored_context: Context | None = None

    @override
    def build(self, context: Context) -> Children:
        raise NotImplementedError(
            "Called build on TemplateComponent without implementation"
        )

    @override
    def full_build(self, context: Context) -> list[Component]:
        # store a copy of the context in the composed TemplateComponent
        # do not build the children until render time
        return children_to_list(self.compose(context.copy(), self.children))

    @override
    def render(self) -> htpy.Node:
        if not issubclass(self.builder, TemplateBuilder):
            raise ValueError("TemplateComponent must be built with TemplateBuilder.")
        if self.stored_context is None:
            raise ValueError(
                "TemplateComponent must have stored_context set before rendering."
            )
        result = self.builder(self.stored_context).build(self)
        return (child.render() for child in result)

    @override
    def compose(self, context: Context, children: Children) -> Children:
        if self.is_built:
            return children
        return self.copy(
            children=children,
            modifiers=[self.attributes, self.modifiers],
            is_built=True,
            stored_context=context,
        )


class Provider(Component):
    """Component that provides a value to its children."""

    provides: Consumable

    @override
    def provide(self, context: Context) -> None:
        super().provide(context)
        context.provide(self.provides)

    @override
    def build(self, context: Context) -> Children:
        return self.children
