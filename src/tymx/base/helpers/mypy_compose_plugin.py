from typing import Any

from mypy.plugin import Plugin
from mypy.plugins.attrs import (
    attr_attrib_makers,
    attr_class_makers,
    attr_dataclass_makers,
)

# These work just like `attr.dataclass`.
attr_dataclass_makers.add("my_module.method_looks_like_attr_dataclass")

# This works just like `attr.s`.
attr_class_makers.add("my_module.method_looks_like_attr_s")

# These are our `attr.ib` makers.
attr_attrib_makers.add("my_module.method_looks_like_attrib")


class ComposePlugin(Plugin):
    # Our plugin does nothing but it has to exist so this file gets loaded.
    pass


def plugin(version: Any) -> type[Plugin]:
    return ComposePlugin
