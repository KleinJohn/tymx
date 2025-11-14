from typing import Iterable, Self, TypeAlias, Union
from abc import ABCMeta, abstractmethod
import htpy


ComponentLike: TypeAlias = Union["ComponentBase", type["ComponentBase"], str]
ComponentOrComponents: TypeAlias = Union[None, ComponentLike, Iterable[ComponentLike]]


class Context:
    pass


def _component_validate_child(child: ComponentLike) -> "ComponentBase":
    if isinstance(child, type):
        return child()
    elif isinstance(child, str):
        return Text(child)
    return child


def _fill_component_children(
    component: "ComponentBase",
    children: ComponentOrComponents,
) -> None:
    if not children:
        return
    if isinstance(children, Iterable):
        component._children.extend(  # type: ignore
            map(_component_validate_child, children)
        )
    else:
        component._children.append(_component_validate_child(children))  # type: ignore


class ComponentBaseMeta(type):

    def __getitem__(cls, *children: ComponentOrComponents) -> "ComponentBase":
        instance = cls()
        _fill_component_children(instance, *children)
        return instance

    def __str__(cls) -> str:
        return cls.__name__


class AbstractComponentBaseMeta(ABCMeta, ComponentBaseMeta):
    pass


class AbstractComponentMeta(AbstractComponentBaseMeta):
    def __getitem__(cls, *children: ComponentOrComponents) -> "Component":
        instance = cls()
        _fill_component_children(instance, *children)
        return instance


class AbstractDocumentComponentMeta(AbstractComponentBaseMeta):
    def __getitem__(cls, *children: ComponentOrComponents) -> "DocumentLevelComponent":
        instance = cls()
        _fill_component_children(instance, *children)
        return instance


class AbstractHtmlComponentMeta(AbstractComponentMeta):
    def __getitem__(cls, *children: ComponentOrComponents) -> "HtmlComponent":
        instance = cls()
        _fill_component_children(instance, *children)
        return instance


class ComponentBase(metaclass=AbstractComponentBaseMeta):
    is_html_element = False

    # All Components that allow zero children have to provide an empty constructor.
    def __init__(self, *, child: ComponentOrComponents = None):
        super().__init__()
        self._children: list["ComponentBase"] = []
        _fill_component_children(self, child)

    def __getitem__(self, *children: ComponentOrComponents) -> Self:
        _fill_component_children(self, *children)
        return self

    @abstractmethod
    def build(self, context: Context) -> "ComponentBase":
        raise NotImplementedError()

    def render(self, context: Context) -> htpy.Node:
        return self.build(context).render(context)

    @property
    def children(self) -> list["ComponentBase"]:
        return self._children

    def __str__(self) -> str:
        if not self._children:
            return self.__class__.__name__
        return f"{self.__class__.__name__}({", ".join(map(str, self._children))})"


class Component(ComponentBase, metaclass=AbstractComponentMeta):

    @abstractmethod
    def build(self, context: Context) -> "ComponentBase":
        raise NotImplementedError()


# Reserved for document-level components like Html, Head, Body, etc.
class DocumentLevelComponent(ComponentBase, metaclass=AbstractDocumentComponentMeta):
    element: htpy.Element

    def build(self, context: Context) -> Self:
        return self

    def render(self, context: Context) -> htpy.Renderable:
        return self.element[
            (child.build(context).render(context) for child in self.children)
        ]


class LeafComponent(Component):
    def __getitem__(
        self, *children: ComponentLike | Iterable["ComponentLike"] | None
    ) -> ComponentBase:
        if children:
            raise ValueError(
                f"{self.__class__.__name__} does not accept any children, got {len(children)}"
            )
        return super().__getitem__(*children)


class SingleChildComponent(Component):
    @property
    def child(self) -> ComponentBase:
        return self._children[0]

    def __getitem__(
        self, *children: ComponentLike | Iterable["ComponentLike"] | None
    ) -> ComponentBase:
        if len(children) != 1:
            raise ValueError(
                f"{self.__class__.__name__} only accepts a single child, got {len(children)}"
            )
        return super().__getitem__(*children)


class Text(LeafComponent):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def build(self, context: Context) -> "ComponentBase":
        return self

    def render(self, context: Context) -> htpy.Node:
        return self.text

    def __str__(self) -> str:
        return self.text


class HtmlBaseComponent(Component, metaclass=AbstractHtmlComponentMeta):
    is_html_element = True
    element: htpy.BaseElement

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        # set is_html to False for subclasses of children of HtmlComponent
        if HtmlBaseComponent in cls.__mro__[3:]:
            cls.is_html_element = False

    def build(self, context: Context) -> "ComponentBase":
        return self


class HtmlComponent(HtmlBaseComponent):
    element: htpy.Element  # type: ignore

    def render(self, context: Context) -> htpy.Node:
        return self.element[
            (child.build(context).render(context) for child in self.children)
        ]


class HtmlLeafComponent(HtmlBaseComponent):
    element: htpy.VoidElement  # type: ignore

    def render(self, context: Context) -> htpy.Node:
        return self.element


class Html(DocumentLevelComponent):
    element = htpy.html


class Body(DocumentLevelComponent):
    element = htpy.body


class Head(DocumentLevelComponent):
    element = htpy.head


class Div(HtmlComponent):
    element = htpy.div


class Span(HtmlComponent):
    element = htpy.span


class Area(HtmlLeafComponent):
    element = htpy.area


class Br(HtmlLeafComponent):
    element = htpy.br


class A(HtmlComponent):
    element = htpy.a


class Abbr(HtmlComponent):
    element = htpy.abbr


class Address(HtmlComponent):
    element = htpy.address


class Article(HtmlComponent):
    element = htpy.article


class Aside(HtmlComponent):
    element = htpy.aside


class Audio(HtmlComponent):
    element = htpy.audio


class B(HtmlComponent):
    element = htpy.b


class Bdi(HtmlComponent):
    element = htpy.bdi


class Bdo(HtmlComponent):
    element = htpy.bdo


class Blockquote(HtmlComponent):
    element = htpy.blockquote


class Button(HtmlComponent):
    element = htpy.button


class Canvas(HtmlComponent):
    element = htpy.canvas


class Caption(HtmlComponent):
    element = htpy.caption


class Cite(HtmlComponent):
    element = htpy.cite


class Code(HtmlComponent):
    element = htpy.code


class Col(HtmlLeafComponent):
    element = htpy.col


class Colgroup(HtmlComponent):
    element = htpy.colgroup


class Data(HtmlComponent):
    element = htpy.data


class Datalist(HtmlComponent):
    element = htpy.datalist


class Dd(HtmlComponent):
    element = htpy.dd


class Del(HtmlComponent):
    element = htpy.del_


class Details(HtmlComponent):
    element = htpy.details


class Dfn(HtmlComponent):
    element = htpy.dfn


class Dialog(HtmlComponent):
    element = htpy.dialog


class Dl(HtmlComponent):
    element = htpy.dl


class Dt(HtmlComponent):
    element = htpy.dt


class Em(HtmlComponent):
    element = htpy.em


class Embed(HtmlLeafComponent):
    element = htpy.embed


class Fieldset(HtmlComponent):
    element = htpy.fieldset


class Figcaption(HtmlComponent):
    element = htpy.figcaption


class Figure(HtmlComponent):
    element = htpy.figure


class Footer(HtmlComponent):
    element = htpy.footer


class Form(HtmlComponent):
    element = htpy.form


class H1(HtmlComponent):
    element = htpy.h1


class H2(HtmlComponent):
    element = htpy.h2


class H3(HtmlComponent):
    element = htpy.h3


class H4(HtmlComponent):
    element = htpy.h4


class H5(HtmlComponent):
    element = htpy.h5


class H6(HtmlComponent):
    element = htpy.h6


class Header(HtmlComponent):
    element = htpy.header


class Hgroup(HtmlComponent):
    element = htpy.hgroup


class Hr(HtmlLeafComponent):
    element = htpy.hr


class I(HtmlComponent):
    element = htpy.i


class Iframe(HtmlComponent):
    element = htpy.iframe


class Img(HtmlLeafComponent):
    element = htpy.img


class Input(HtmlLeafComponent):
    element = htpy.input


class Ins(HtmlComponent):
    element = htpy.ins


class Kbd(HtmlComponent):
    element = htpy.kbd


class Label(HtmlComponent):
    element = htpy.label


class Legend(HtmlComponent):
    element = htpy.legend


class Li(HtmlComponent):
    element = htpy.li


class Link(HtmlLeafComponent):
    element = htpy.link


class Main(HtmlComponent):
    element = htpy.main


class Map(HtmlComponent):
    element = htpy.map


class Mark(HtmlComponent):
    element = htpy.mark


class Math(HtmlComponent):
    element = htpy.math


class Menu(HtmlComponent):
    element = htpy.menu


class Meta(HtmlLeafComponent):
    element = htpy.meta


class Meter(HtmlComponent):
    element = htpy.meter


class Nav(HtmlComponent):
    element = htpy.nav


class Noscript(HtmlComponent):
    element = htpy.noscript


class Object(HtmlComponent):
    element = htpy.object


class Ol(HtmlComponent):
    element = htpy.ol


class Optgroup(HtmlComponent):
    element = htpy.optgroup


class Option(HtmlComponent):
    element = htpy.option


class Output(HtmlComponent):
    element = htpy.output


class P(HtmlComponent):
    element = htpy.p


class Picture(HtmlComponent):
    element = htpy.picture


class Pre(HtmlComponent):
    element = htpy.pre


class Progress(HtmlComponent):
    element = htpy.progress


class Q(HtmlComponent):
    element = htpy.q


class Rp(HtmlComponent):
    element = htpy.rp


class Rt(HtmlComponent):
    element = htpy.rt


class Ruby(HtmlComponent):
    element = htpy.ruby


class S(HtmlComponent):
    element = htpy.s


class Samp(HtmlComponent):
    element = htpy.samp


class Script(HtmlComponent):
    element = htpy.script


class Section(HtmlComponent):
    element = htpy.section


class Select(HtmlComponent):
    element = htpy.select


class Small(HtmlComponent):
    element = htpy.small


class Source(HtmlLeafComponent):
    element = htpy.source


class Strong(HtmlComponent):
    element = htpy.strong


class Style(HtmlComponent):
    element = htpy.style


class Sub(HtmlComponent):
    element = htpy.sub


class Svg(HtmlComponent):
    element = htpy.svg


class Summary(HtmlComponent):
    element = htpy.summary


class Sup(HtmlComponent):
    element = htpy.sup


class Table(HtmlComponent):
    element = htpy.table


class Tbody(HtmlComponent):
    element = htpy.tbody


class Td(HtmlComponent):
    element = htpy.td


class Template(HtmlComponent):
    element = htpy.template


class Textarea(HtmlComponent):
    element = htpy.textarea


class Tfoot(HtmlComponent):
    element = htpy.tfoot


class Th(HtmlComponent):
    element = htpy.th


class Thead(HtmlComponent):
    element = htpy.thead


class Time(HtmlComponent):
    element = htpy.time


class Title(HtmlComponent):
    element = htpy.title


class Tr(HtmlComponent):
    element = htpy.tr


class Track(HtmlLeafComponent):
    element = htpy.track


class U(HtmlComponent):
    element = htpy.u


class Ul(HtmlComponent):
    element = htpy.ul


class Var(HtmlComponent):
    element = htpy.var


class Video(HtmlComponent):
    element = htpy.video


class Wbr(HtmlLeafComponent):
    element = htpy.wbr


class Base(HtmlLeafComponent):
    element = htpy.base
