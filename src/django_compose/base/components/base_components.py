from functools import reduce
from typing import Iterable, Self, TypeAlias, Union, final
from abc import ABCMeta, abstractmethod
import htpy

from django_compose.base.modifiers import Tag


ComponentBaseLike: TypeAlias = Union["ComponentBase", type["ComponentBase"], str]
ComponentOrComponentsBase: TypeAlias = Union[
    None, ComponentBaseLike, Iterable[ComponentBaseLike]
]
ComponentLike: TypeAlias = Union["Component", type["Component"], str]
ComponentOrComponents: TypeAlias = Union[None, ComponentLike, Iterable[ComponentLike]]


class Context:
    pass


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
        self._context: Context | None = None

    def __getitem__(self, children: ComponentOrComponentsBase) -> Self:
        self._children = _fill_component_children(children)
        return self

    def __str__(self) -> str:
        if not self._children:
            return self.__class__.__name__
        return f"{self.__class__.__name__}({", ".join(str(child) for child in self._children)})"

    def copy_with_children(self, children: Iterable["ComponentBase"]) -> Self:
        return self.__class__(
            *self._tags,
            children=children,
            **self._htpy_kwargs,
        )

    def full_build(self, context: Context) -> "ComponentBase":
        self._context = context
        built_self = self.build(context)
        self._context = None
        return built_self

    @abstractmethod
    def build(self, context: Context) -> "ComponentBase":
        raise NotImplementedError()

    def render(self, context: Context) -> htpy.Node:
        root = self.full_build(context)
        return root.render(context)

    def compile_tags(self) -> Tag:
        return reduce(lambda a, b: a | b, self._tags, Tag())

    @property
    def children(self) -> Iterable["ComponentBase"]:
        if not self._context:
            return self._children
        return (child.full_build(self._context) for child in self._children)

    @property
    def tags(self) -> Iterable[Tag]:
        return self._tags


class Component(ComponentBase, metaclass=AbstractComponentMeta):

    @abstractmethod
    def build(self, context: Context) -> "ComponentBase":
        raise NotImplementedError()


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
        return self

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

    def build(self, context: Context) -> "ComponentBase":
        return Text(self.text)

    def render(self, context: Context) -> htpy.Node:
        return self.text

    def __str__(self) -> str:
        return f'"{self.text}"'
