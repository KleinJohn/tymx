from typing import Iterable, Self, TypeAlias, Union, final
from abc import ABCMeta, abstractmethod
import htpy

from django_compose.base.modifiers import Modifier


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
    if isinstance(children, Iterable):
        return tuple(map(_component_validate_child, children))
    else:
        return (_component_validate_child(children),)  # type: ignore


class ComponentBaseMeta(type):

    def __getitem__(cls, *children: ComponentOrComponentsBase) -> "ComponentBase":
        return cls(children=children)

    def __str__(cls) -> str:
        return cls.__name__


class AbstractComponentBaseMeta(ABCMeta, ComponentBaseMeta):
    pass


class AbstractComponentMeta(AbstractComponentBaseMeta):
    def __getitem__(cls, *children: ComponentOrComponentsBase) -> "Component":
        return cls(children=children)


class ComponentBase(metaclass=AbstractComponentBaseMeta):
    is_html_element = False

    # All Components that allow zero children have to provide an empty constructor.
    def __init__(
        self,
        *modifiers: Modifier | Iterable[Modifier],
        children: ComponentOrComponentsBase = None,
        **htpy_kwargs: str,
    ) -> None:
        self._modifiers: list[Modifier] = []
        for modifier in modifiers:
            if isinstance(modifier, Iterable):
                self._modifiers.extend(modifier)
            else:
                self._modifiers.append(modifier)
        self._children: tuple["ComponentBase", ...] = _fill_component_children(children)
        self._htpy_kwargs = htpy_kwargs

    def __getitem__(self, *children: ComponentOrComponentsBase) -> Self:
        _fill_component_children(self, *children)
        return self

    @abstractmethod
    def build(self, context: Context) -> "ComponentBase":
        raise NotImplementedError()

    def render(self, context: Context) -> htpy.Node:
        return self.build(context).render(context)

    @property
    def children(self) -> tuple["ComponentBase", ...]:
        return self._children

    def __str__(self) -> str:
        if not self._children:
            return self.__class__.__name__
        return f"{self.__class__.__name__}({", ".join(map(str, self._children))})"


class Component(ComponentBase, metaclass=AbstractComponentMeta):

    @abstractmethod
    def build(self, context: Context) -> "ComponentBase":
        raise NotImplementedError()


class AbstractLeafComponentMeta(AbstractComponentMeta):
    def __getitem__(cls, *children: ComponentOrComponentsBase) -> "LeafComponent":
        instance = cls()
        if children:
            raise ValueError(
                f"{cls.__name__} does not accept any children, got {len(children)}"
            )
        return instance


class LeafComponent(Component, metaclass=AbstractLeafComponentMeta):
    def __getitem__(
        self, *children: ComponentBaseLike | Iterable["ComponentBaseLike"] | None
    ) -> ComponentBase:
        if children:
            raise ValueError(
                f"{self.__class__.__name__} does not accept any children, got {len(children)}"
            )
        return self


class AbstractSingleChildComponentMeta(AbstractComponentMeta):
    def __getitem__(
        cls, *children: ComponentOrComponentsBase
    ) -> "SingleChildComponent":
        if len(children) != 1:
            raise ValueError(
                f"{cls.__name__} only accepts a single child, got {len(children)}"
            )
        return cls(children=children)


class SingleChildComponent(Component, metaclass=AbstractSingleChildComponentMeta):
    @property
    def child(self) -> ComponentBase:
        return self._children[0]

    def __getitem__(
        self, *children: ComponentBaseLike | Iterable["ComponentBaseLike"] | None
    ) -> ComponentBase:
        if len(children) != 1:
            raise ValueError(
                f"{self.__class__.__name__} only accepts a single child, got {len(children)}"
            )
        return super().__getitem__(*children)


class AbstractTextComponentMeta(AbstractLeafComponentMeta):
    def __getitem__(cls, *children: ComponentOrComponentsBase) -> "Text":
        if isinstance(children, str):
            return Text(children)
        if len(children) != 1 or not isinstance(children[0], str):
            raise ValueError(
                f"{cls.__name__} only accepts a single string child, got {children}"
            )
        return Text(children[0])


@final
class Text(LeafComponent, metaclass=AbstractTextComponentMeta):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def build(self, context: Context) -> "ComponentBase":
        return self

    def render(self, context: Context) -> htpy.Node:
        return self.text

    def __str__(self) -> str:
        return self.text
