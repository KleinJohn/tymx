"""
Configuration module for django-compose.

This module provides globally accessible configuration variables that can be
overwritten from outside the library.
"""

from collections.abc import Callable

from django_compose.base.attributes import Attribute, classes
from django_compose.base.theme import Theme, ThemeType

# Default attribute that can be overridden by external code
attribute_string_handler: Callable[[str], Attribute] = lambda s: classes(s)
default_theme = Theme(framework=ThemeType.HTML)

__all__ = ["attribute_string_handler", "default_theme"]
