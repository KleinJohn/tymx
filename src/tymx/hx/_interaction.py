from attrs import field

from tymx.base.helpers.converters import enum_converter
from tymx.base.modifiers.base_modifiers import Modifier
from tymx.hx._helpers import HttpMethod


class Interaction(Modifier):
    method: HttpMethod = field(converter=enum_converter(HttpMethod))
