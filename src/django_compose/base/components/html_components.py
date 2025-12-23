from typing import Protocol, override
from django_compose.base.modifiers.base_modifiers import Attributes
from .base_components import *


class IsHtml(Protocol):
    element: htpy.Element
    attributes: Attributes
    children: list[ComponentBase]
    _htpy_kwargs: dict[str, str]

    def __getitem__(self, children: Children) -> Self: ...

    def render(self) -> htpy.Node: ...


class RendersHtmlMixin(RenderableComponentMixin):
    element: htpy.Element

    def render(self: IsHtml) -> htpy.Renderable:
        return self.element(**self.attributes.values(), **self._htpy_kwargs)[
            (child.render() for child in self.children)
        ]


class DocumentLevelComponent(RendersHtmlMixin, ComponentBase):
    """Reserved for document-level components like Html, Head, Body."""

    def full_build(self, context: Context) -> "DocumentLevelComponent":
        build_result = super().full_build(context)
        if not isinstance(build_result, DocumentLevelComponent):
            raise TypeError(
                f"DocumentLevelComponent.build must return a DocumentLevelComponent, got {type(build_result)}"
            )
        return build_result


class HtmlComponent(RendersHtmlMixin, Component):

    def full_build(self, context: Context) -> "HtmlComponent":
        build_result = super().full_build(context)
        if not isinstance(build_result, HtmlComponent):
            raise TypeError(
                f"HtmlComponent.build must return a HtmlComponent, got {type(build_result)}"
            )
        return build_result


class HtmlVoidComponent(VoidComponentMixin, HtmlComponent):
    element: htpy.VoidElement  # type: ignore

    @override
    def render(self) -> htpy.Renderable:
        return self.element(**self.attributes.values(), **self._htpy_kwargs)


@final
class Html(DocumentLevelComponent):
    element = htpy.html


@final
class Body(DocumentLevelComponent):
    element = htpy.body


@final
class Head(DocumentLevelComponent):
    element = htpy.head


@final
class Div(HtmlComponent):
    element = htpy.div


@final
class Span(HtmlComponent):
    element = htpy.span


@final
class Area(HtmlVoidComponent):
    element = htpy.area


@final
class Br(HtmlVoidComponent):
    element = htpy.br


@final
class A(HtmlComponent):
    element = htpy.a


@final
class Abbr(HtmlComponent):
    element = htpy.abbr


@final
class Address(HtmlComponent):
    element = htpy.address


@final
class Article(HtmlComponent):
    element = htpy.article


@final
class Aside(HtmlComponent):
    element = htpy.aside


@final
class Audio(HtmlComponent):
    element = htpy.audio


@final
class B(HtmlComponent):
    element = htpy.b


@final
class Bdi(HtmlComponent):
    element = htpy.bdi


@final
class Bdo(HtmlComponent):
    element = htpy.bdo


@final
class Blockquote(HtmlComponent):
    element = htpy.blockquote


@final
class Button(HtmlComponent):
    element = htpy.button


@final
class Canvas(HtmlComponent):
    element = htpy.canvas


@final
class Caption(HtmlComponent):
    element = htpy.caption


@final
class Cite(HtmlComponent):
    element = htpy.cite


@final
class Code(HtmlComponent):
    element = htpy.code


@final
class Col(HtmlVoidComponent):
    element = htpy.col


@final
class Colgroup(HtmlComponent):
    element = htpy.colgroup


@final
class Data(HtmlComponent):
    element = htpy.data


@final
class Datalist(HtmlComponent):
    element = htpy.datalist


@final
class Dd(HtmlComponent):
    element = htpy.dd


@final
class Del(HtmlComponent):
    element = htpy.del_


@final
class Details(HtmlComponent):
    element = htpy.details


@final
class Dfn(HtmlComponent):
    element = htpy.dfn


@final
class Dialog(HtmlComponent):
    element = htpy.dialog


@final
class Dl(HtmlComponent):
    element = htpy.dl


@final
class Dt(HtmlComponent):
    element = htpy.dt


@final
class Em(HtmlComponent):
    element = htpy.em


@final
class Embed(HtmlVoidComponent):
    element = htpy.embed


@final
class Fieldset(HtmlComponent):
    element = htpy.fieldset


@final
class Figcaption(HtmlComponent):
    element = htpy.figcaption


@final
class Figure(HtmlComponent):
    element = htpy.figure


@final
class Footer(HtmlComponent):
    element = htpy.footer


@final
class Form(HtmlComponent):
    element = htpy.form


@final
class H1(HtmlComponent):
    element = htpy.h1


@final
class H2(HtmlComponent):
    element = htpy.h2


@final
class H3(HtmlComponent):
    element = htpy.h3


@final
class H4(HtmlComponent):
    element = htpy.h4


@final
class H5(HtmlComponent):
    element = htpy.h5


@final
class H6(HtmlComponent):
    element = htpy.h6


@final
class Header(HtmlComponent):
    element = htpy.header


@final
class Hgroup(HtmlComponent):
    element = htpy.hgroup


@final
class Hr(HtmlVoidComponent):
    element = htpy.hr


@final
class I(HtmlComponent):
    element = htpy.i


@final
class Iframe(HtmlComponent):
    element = htpy.iframe


@final
class Img(HtmlVoidComponent):
    element = htpy.img


@final
class Input(HtmlVoidComponent):
    element = htpy.input


@final
class Ins(HtmlComponent):
    element = htpy.ins


@final
class Kbd(HtmlComponent):
    element = htpy.kbd


@final
class Label(HtmlComponent):
    element = htpy.label


@final
class Legend(HtmlComponent):
    element = htpy.legend


@final
class Li(HtmlComponent):
    element = htpy.li


@final
class Link(HtmlVoidComponent):
    element = htpy.link


@final
class Main(HtmlComponent):
    element = htpy.main


@final
class Map(HtmlComponent):
    element = htpy.map


@final
class Mark(HtmlComponent):
    element = htpy.mark


@final
class Math(HtmlComponent):
    element = htpy.math


@final
class Menu(HtmlComponent):
    element = htpy.menu


@final
class Meta(HtmlVoidComponent):
    element = htpy.meta


@final
class Meter(HtmlComponent):
    element = htpy.meter


@final
class Nav(HtmlComponent):
    element = htpy.nav


@final
class Noscript(HtmlComponent):
    element = htpy.noscript


@final
class Object(HtmlComponent):
    element = htpy.object


@final
class Ol(HtmlComponent):
    element = htpy.ol


@final
class Optgroup(HtmlComponent):
    element = htpy.optgroup


@final
class Option(HtmlComponent):
    element = htpy.option


@final
class Output(HtmlComponent):
    element = htpy.output


@final
class P(HtmlComponent):
    element = htpy.p


@final
class Picture(HtmlComponent):
    element = htpy.picture


@final
class Pre(HtmlComponent):
    element = htpy.pre


@final
class Progress(HtmlComponent):
    element = htpy.progress


@final
class Q(HtmlComponent):
    element = htpy.q


@final
class Rp(HtmlComponent):
    element = htpy.rp


@final
class Rt(HtmlComponent):
    element = htpy.rt


@final
class Ruby(HtmlComponent):
    element = htpy.ruby


@final
class S(HtmlComponent):
    element = htpy.s


@final
class Samp(HtmlComponent):
    element = htpy.samp


@final
class Script(HtmlComponent):
    element = htpy.script


@final
class Section(HtmlComponent):
    element = htpy.section


@final
class Select(HtmlComponent):
    element = htpy.select


@final
class Small(HtmlComponent):
    element = htpy.small


@final
class Source(HtmlVoidComponent):
    element = htpy.source


@final
class Strong(HtmlComponent):
    element = htpy.strong


@final
class Style(HtmlComponent):
    element = htpy.style


@final
class Sub(HtmlComponent):
    element = htpy.sub


@final
class Svg(HtmlComponent):
    element = htpy.svg


@final
class Summary(HtmlComponent):
    element = htpy.summary


@final
class Sup(HtmlComponent):
    element = htpy.sup


@final
class Table(HtmlComponent):
    element = htpy.table


@final
class Tbody(HtmlComponent):
    element = htpy.tbody


@final
class Td(HtmlComponent):
    element = htpy.td


@final
class Template(HtmlComponent):
    element = htpy.template


@final
class Textarea(HtmlComponent):
    element = htpy.textarea


@final
class Tfoot(HtmlComponent):
    element = htpy.tfoot


@final
class Th(HtmlComponent):
    element = htpy.th


@final
class Thead(HtmlComponent):
    element = htpy.thead


@final
class Time(HtmlComponent):
    element = htpy.time


@final
class Title(HtmlComponent):
    element = htpy.title


@final
class Tr(HtmlComponent):
    element = htpy.tr


@final
class Track(HtmlVoidComponent):
    element = htpy.track


@final
class U(HtmlComponent):
    element = htpy.u


@final
class Ul(HtmlComponent):
    element = htpy.ul


@final
class Var(HtmlComponent):
    element = htpy.var


@final
class Video(HtmlComponent):
    element = htpy.video


@final
class Wbr(HtmlVoidComponent):
    element = htpy.wbr


@final
class Base(HtmlVoidComponent):
    element = htpy.base
