from __future__ import annotations
from functools import reduce
from typing import Iterable, Self, TypeAlias, Union, final, TYPE_CHECKING
from abc import ABCMeta, abstractmethod
import htpy

from django_compose.base.modifiers import Tag

if TYPE_CHECKING:
    from django_compose.base.theme import Theme, ComponentTheme


ComponentBaseLike: TypeAlias = Union["ComponentBase", type["ComponentBase"], str]
ComponentOrComponentsBase: TypeAlias = Union[
    None, ComponentBaseLike, Iterable[ComponentBaseLike]
]
ComponentLike: TypeAlias = Union["Component", type["Component"], str]
ComponentOrComponents: TypeAlias = Union[None, ComponentLike, Iterable[ComponentLike]]


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
    children: ComponentOrComponentsBase,
) -> tuple["ComponentBase", ...]:
    if not children:
        return tuple()
    if isinstance(children, Iterable) and not isinstance(children, str):
        return tuple(map(_component_validate_child, children))
    else:
        return (_component_validate_child(children),)


class ComponentBaseMeta(type):

    def __getitem__(cls, children: ComponentOrComponentsBase) -> "ComponentBase":
        return cls(children=children)

    def __str__(cls) -> str:
        return cls.__name__


class AbstractComponentBaseMeta(ABCMeta, ComponentBaseMeta):
    pass


class AbstractComponentMeta(AbstractComponentBaseMeta):
    def __getitem__(cls, children: ComponentOrComponentsBase) -> "Component":
        return cls(children=children)


class ComponentBase(metaclass=AbstractComponentBaseMeta):
    inherit_tags = True

    # All Components that allow zero children have to provide an empty constructor.
    def __init__(
        self,
        *tags: Tag | Iterable[Tag],
        children: ComponentOrComponentsBase = None,
        **htpy_kwargs: str,
    ) -> None:
        self._tags: list[Tag] = []
        for tag in tags:
            if isinstance(tag, Iterable):
                self._tags.extend(tag)
            else:
                self._tags.append(tag)
        self._children: tuple["ComponentBase", ...] = _fill_component_children(children)
        self._htpy_kwargs: dict[str, str] = htpy_kwargs

    def __getitem__(self, children: ComponentOrComponentsBase) -> Self:
        return self.__class__(
            *self._tags,
            children=_fill_component_children(children),
            **self._htpy_kwargs,
        )

    def __str__(self) -> str:
        if not self._children:
            return self.__class__.__name__
        return f"{self.__class__.__name__}({", ".join(str(child) for child in self._children)})"

    @abstractmethod
    def build(
        self, context: Context, children: ComponentOrComponentsBase
    ) -> "ComponentBase":
        raise NotImplementedError()

    def full_build(self, context: Context) -> "ComponentBase":
        self_built = self.build(context, self._children)
        if self.__class__.inherit_tags:
            self_built.add_tags(self.tags)
        return self_built

    def render(self, context: Context) -> htpy.Node:
        root = self.full_build(context)
        return root.render(context)

    def compile_tags(self) -> Tag:
        return reduce(lambda a, b: a | b, self._tags, Tag())

    def add_tags(self, tags: Iterable[Tag]) -> None:
        # TODO: Merge tags into existing tags
        self._tags.extend(tags)

    @property
    def tags(self) -> Iterable[Tag]:
        return self._tags


class Component(ComponentBase, metaclass=AbstractComponentMeta):

    def __init__(
        self,
        *tags: Tag | Iterable[Tag],
        theme: ComponentTheme | None = None,
        children: ComponentOrComponentsBase = None,
        **htpy_kwargs: str,
    ) -> None:
        super().__init__(*tags, children=children, **htpy_kwargs)
        self.theme = theme

    @abstractmethod
    def build(
        self, context: Context, children: ComponentOrComponentsBase
    ) -> "Component":
        raise NotImplementedError()

    def full_build(self, context: Context) -> "Component":
        children = (child.full_build(context) for child in self._children)
        built_self = self.build(context, children)
        built_self = self.apply_theme(context, built_self)
        return built_self

    def apply_theme(self, context: Context, component: "Component") -> "Component":
        if self.theme:
            component = self.theme.modify_build(context, component)
            if self.__class__.inherit_tags:
                component.add_tags(self.tags)
            component._tags = self.theme.modify_tags(component._tags)
        return component

    def __getitem__(self, children: ComponentOrComponentsBase) -> Self:
        return self.__class__(
            *self._tags,
            children=_fill_component_children(children),
            theme=self.theme,
            **self._htpy_kwargs,
        )


class AbstractLeafComponentMeta(AbstractComponentMeta):
    def __getitem__(cls, children: ComponentOrComponentsBase) -> "LeafComponent":
        if children:
            raise ValueError(
                f"{cls.__name__} does not accept any children, got {children}"
            )
        return cls()


class LeafComponent(Component, metaclass=AbstractLeafComponentMeta):
    def __getitem__(self, children: ComponentOrComponentsBase) -> "LeafComponent":
        if children:
            raise ValueError(
                f"{self.__class__.__name__} does not accept any children, got {children}"
            )
        return super().__getitem__(children)

    @abstractmethod
    def build(self, context: Context, _: ComponentOrComponentsBase) -> "Component":
        raise NotImplementedError()

    @abstractmethod
    def render(self, context: Context) -> htpy.Node:
        raise NotImplementedError()


class AbstractSingleChildComponentMeta(AbstractComponentMeta):
    def __getitem__(cls, children: ComponentOrComponentsBase) -> "SingleChildComponent":
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
        return self._children[0]

    def __getitem__(
        self, children: ComponentOrComponentsBase
    ) -> "SingleChildComponent":
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
    def build(self, context: Context, child: ComponentOrComponentsBase) -> "Component":
        raise NotImplementedError()


class AbstractTextComponentMeta(AbstractLeafComponentMeta):
    def __getitem__(cls, children: ComponentOrComponentsBase) -> "Text":
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

    def build(self, context: Context, _: ComponentOrComponentsBase) -> "Component":
        return Text(self.text)

    def render(self, context: Context) -> htpy.Node:
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
            component._tags = self.theme.modify_tags(component._tags)
        elif context_theme:
            component = context_theme.modify_build(context, component)
            component._tags = context_theme.modify_tags(component._tags)
        return component
